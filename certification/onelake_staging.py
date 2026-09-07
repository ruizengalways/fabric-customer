"""Credential-safe OneLake DFS staging for exact certification artifacts."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path, PurePosixPath
from typing import Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen
from uuid import UUID


DEFAULT_ONELAKE_ENDPOINT = "https://onelake.dfs.fabric.microsoft.com"
_STORAGE_API_VERSION = "2021-06-08"


class OneLakeStagingError(RuntimeError):
    """Fail-closed staging error that never includes bearer-token values."""


@dataclass(frozen=True)
class OneLakeUpload:
    relative_path: str
    size_bytes: int
    sha256: str


def _uuid(value: str, label: str) -> str:
    try:
        return str(UUID(value))
    except ValueError as exc:
        raise OneLakeStagingError(f"{label} must be a UUID") from exc


def _relative_path(value: str) -> str:
    candidate = value.replace("\\", "/").strip("/")
    path = PurePosixPath(candidate)
    if not candidate or path.is_absolute() or ".." in path.parts:
        raise OneLakeStagingError("OneLake relative path must remain below the item root")
    if path.parts[0] not in {"Files", "Tables"}:
        raise OneLakeStagingError("OneLake path must start with Files or Tables")
    return path.as_posix()


class OneLakeDfsClient:
    def __init__(
        self,
        access_token: str,
        *,
        endpoint: str = DEFAULT_ONELAKE_ENDPOINT,
        request_timeout_seconds: int = 120,
    ) -> None:
        token = access_token.strip()
        if not token or "\n" in token or "\r" in token:
            raise OneLakeStagingError("OneLake access token is missing or malformed")
        root = endpoint.rstrip("/")
        parsed = urlparse(root)
        if (
            parsed.scheme != "https"
            or not parsed.netloc
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            raise OneLakeStagingError("OneLake endpoint must be a credential-free HTTPS URL")
        if not (parsed.hostname or "").endswith(".dfs.fabric.microsoft.com"):
            raise OneLakeStagingError("OneLake endpoint must use a Fabric DFS hostname")
        self._token = token
        self._endpoint = root
        self._host = parsed.netloc.lower()
        self._timeout = request_timeout_seconds

    def _url(
        self,
        workspace_id: str,
        item_id: str,
        relative_path: str,
        query: Mapping[str, str] | None = None,
    ) -> str:
        workspace = _uuid(workspace_id, "workspace_id")
        item = _uuid(item_id, "lakehouse_id")
        path = _relative_path(relative_path)
        encoded = "/".join(quote(part, safe="") for part in path.split("/"))
        url = f"{self._endpoint}/{workspace}/{item}/{encoded}"
        if query:
            url += "?" + urlencode(query)
        return url

    def _request(
        self,
        method: str,
        url: str,
        *,
        data: bytes | None = None,
        expected: set[int],
        ignore: set[int] = frozenset(),
    ) -> int:
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.netloc.lower() != self._host:
            raise OneLakeStagingError("OneLake request left the approved endpoint host")
        headers = {
            "Authorization": f"Bearer {self._token}",
            "x-ms-version": _STORAGE_API_VERSION,
            "Content-Length": str(len(data or b"")),
        }
        request = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self._timeout) as response:
                status = int(response.status)
                response.read()
                if status not in expected:
                    raise OneLakeStagingError(
                        f"OneLake {method} returned unexpected HTTP {status}"
                    )
                return status
        except HTTPError as exc:
            exc.read()
            if exc.code in ignore:
                return exc.code
            raise OneLakeStagingError(
                f"OneLake {method} failed with HTTP {exc.code}"
            ) from exc
        except URLError as exc:
            raise OneLakeStagingError(f"OneLake {method} network failure") from exc

    def delete_path(
        self,
        workspace_id: str,
        lakehouse_id: str,
        relative_path: str,
        *,
        recursive: bool = False,
    ) -> None:
        query = {"recursive": "true"} if recursive else None
        self._request(
            "DELETE",
            self._url(workspace_id, lakehouse_id, relative_path, query),
            expected={200},
            ignore={404},
        )

    def ensure_directory(self, workspace_id: str, lakehouse_id: str, relative_path: str) -> None:
        path = _relative_path(relative_path)
        self._request(
            "PUT",
            self._url(workspace_id, lakehouse_id, path, {"resource": "directory"}),
            expected={201},
            ignore={409},
        )

    def upload_bytes(
        self,
        workspace_id: str,
        lakehouse_id: str,
        relative_path: str,
        content: bytes,
    ) -> OneLakeUpload:
        path = _relative_path(relative_path)
        pure = PurePosixPath(path)
        parents: list[PurePosixPath] = []
        cursor = pure.parent
        while cursor.as_posix() not in {".", "Files", "Tables"}:
            parents.append(cursor)
            cursor = cursor.parent
        for parent in reversed(parents):
            self.ensure_directory(workspace_id, lakehouse_id, parent.as_posix())

        file_url = self._url(workspace_id, lakehouse_id, path)
        self._request("DELETE", file_url, expected={200}, ignore={404})
        self._request(
            "PUT",
            self._url(workspace_id, lakehouse_id, path, {"resource": "file"}),
            data=b"",
            expected={201},
        )
        if content:
            self._request(
                "PATCH",
                self._url(
                    workspace_id,
                    lakehouse_id,
                    path,
                    {"action": "append", "position": "0"},
                ),
                data=content,
                expected={202},
            )
        self._request(
            "PATCH",
            self._url(
                workspace_id,
                lakehouse_id,
                path,
                {"action": "flush", "position": str(len(content))},
            ),
            data=b"",
            expected={200},
        )
        return OneLakeUpload(
            relative_path=path,
            size_bytes=len(content),
            sha256=hashlib.sha256(content).hexdigest(),
        )

    def upload_tree(
        self,
        workspace_id: str,
        lakehouse_id: str,
        *,
        local_root: str | Path,
        remote_root: str,
        replace_remote_root: bool = False,
    ) -> tuple[OneLakeUpload, ...]:
        source = Path(local_root)
        if not source.is_dir():
            raise OneLakeStagingError(f"local staging root does not exist: {source}")
        remote = _relative_path(remote_root)
        if replace_remote_root:
            self.delete_path(workspace_id, lakehouse_id, remote, recursive=True)
        uploads: list[OneLakeUpload] = []
        for path in sorted(item for item in source.rglob("*") if item.is_file()):
            relative = path.relative_to(source).as_posix()
            uploads.append(
                self.upload_bytes(
                    workspace_id,
                    lakehouse_id,
                    f"{remote}/{relative}",
                    path.read_bytes(),
                )
            )
        return tuple(uploads)


def staging_manifest(uploads: tuple[OneLakeUpload, ...]) -> dict[str, object]:
    return {
        "contains_secret_values": False,
        "file_count": len(uploads),
        "total_bytes": sum(item.size_bytes for item in uploads),
        "files": [
            {"relative_path": item.relative_path, "size_bytes": item.size_bytes, "sha256": item.sha256}
            for item in uploads
        ],
    }


__all__ = [
    "DEFAULT_ONELAKE_ENDPOINT",
    "OneLakeDfsClient",
    "OneLakeStagingError",
    "OneLakeUpload",
    "staging_manifest",
]
