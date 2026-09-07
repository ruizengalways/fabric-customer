"""Create or update the repository-owned certification Notebook and Data Pipeline.

This deployer is intentionally narrow:
- only DEV/UAT certification workspaces are accepted;
- Fabric API auth defaults to the current ``az login`` user and may alternatively read
  an approved access token from an environment variable;
- Fabric-native SQL runtime bindings contain only non-secret server/database identity;
- the existing Key Vault secret-name lane remains optional for enterprise environments;
- exact display-name duplicates fail closed instead of guessing an item;
- Microsoft Fabric long-running operations are polled to a terminal state.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from uuid import UUID

try:
    from render_fabric_items import (
        DEFAULT_INPUTS_ROOT,
        RUNTIME_AUTH_FABRIC_USER,
        RUNTIME_AUTH_KEY_VAULT,
        render_notebook_payload,
        render_pipeline_create_payload,
    )
except ModuleNotFoundError:  # pragma: no cover - package-style import fallback
    from .render_fabric_items import (
        DEFAULT_INPUTS_ROOT,
        RUNTIME_AUTH_FABRIC_USER,
        RUNTIME_AUTH_KEY_VAULT,
        render_notebook_payload,
        render_pipeline_create_payload,
    )


API_ROOT = "https://api.fabric.microsoft.com/v1"
FABRIC_API_RESOURCE = "https://api.fabric.microsoft.com"
API_AUTH_AZURE_CLI = "azure-cli"
API_AUTH_ENV_TOKEN = "env-token"
DEFAULT_ACCESS_TOKEN_ENV_VAR = "FABRIC_ACCESS_TOKEN"
DEFAULT_NOTEBOOK_NAME = "framework-certification-worker"
DEFAULT_PIPELINE_NAME = "framework-certification-child"


class FabricDeploymentError(RuntimeError):
    """Fail-closed deployment error without credential material."""


@dataclass(frozen=True)
class HttpResult:
    status: int
    headers: Mapping[str, str]
    body: object | None


def _uuid(value: str, label: str) -> str:
    try:
        return str(UUID(value))
    except ValueError as exc:
        raise FabricDeploymentError(f"{label} must be a UUID") from exc


def _canonical_sha256(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _header(headers: Mapping[str, str], name: str) -> str | None:
    target = name.lower()
    for key, value in headers.items():
        if key.lower() == target:
            return value
    return None


def _retry_after(headers: Mapping[str, str], *, default: int = 2) -> int:
    raw = _header(headers, "Retry-After")
    if raw is None:
        return default
    try:
        return max(1, min(60, int(raw)))
    except ValueError:
        return default


def _error_summary(body: object | None) -> str:
    if isinstance(body, Mapping):
        code = body.get("errorCode") or body.get("code")
        message = body.get("message")
        if code and message:
            return f"{code}: {message}"
        if message:
            return str(message)
    return "Fabric API request failed"


def _azure_cli_access_token() -> str:
    """Use the current interactive Azure CLI session without printing the token."""

    command = [
        "az",
        "account",
        "get-access-token",
        "--resource",
        FABRIC_API_RESOURCE,
        "--query",
        "accessToken",
        "-o",
        "tsv",
    ]
    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise FabricDeploymentError(
            "Azure CLI was not found; install az and run az login, or use --auth-mode env-token"
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise FabricDeploymentError(
            "Azure CLI could not obtain a Fabric API token; run az login (or az login --allow-no-subscriptions)"
        ) from exc
    token = completed.stdout.strip()
    if not token or "\n" in token or "\r" in token:
        raise FabricDeploymentError("Azure CLI returned an empty or malformed Fabric API token")
    return token


class FabricApiClient:
    def __init__(
        self,
        access_token: str,
        *,
        api_root: str = API_ROOT,
        request_timeout_seconds: int = 60,
        lro_timeout_seconds: int = 900,
        sleep_fn: Callable[[float], None] = time.sleep,
        monotonic_fn: Callable[[], float] = time.monotonic,
    ) -> None:
        token = access_token.strip()
        if not token or "\n" in token or "\r" in token:
            raise FabricDeploymentError("Fabric access token is missing or malformed")
        root = api_root.rstrip("/")
        parsed = urlparse(root)
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
            raise FabricDeploymentError("Fabric API root must be a credential-free HTTPS URL")
        self._token = token
        self._api_root = root
        self._api_host = parsed.netloc.lower()
        self._request_timeout_seconds = request_timeout_seconds
        self._lro_timeout_seconds = lro_timeout_seconds
        self._sleep = sleep_fn
        self._monotonic = monotonic_fn

    def _absolute_url(self, path_or_url: str) -> str:
        url = path_or_url if path_or_url.startswith("https://") else f"{self._api_root}/{path_or_url.lstrip('/')}"
        parsed = urlparse(url)
        if (
            parsed.scheme != "https"
            or parsed.netloc.lower() != self._api_host
            or parsed.username
            or parsed.password
        ):
            raise FabricDeploymentError("Fabric API continuation/operation URL left the approved API host")
        return url

    def _request(
        self,
        method: str,
        path_or_url: str,
        payload: object | None = None,
    ) -> HttpResult:
        url = self._absolute_url(path_or_url)
        data = None
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
        }
        if payload is not None:
            data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            headers["Content-Type"] = "application/json"

        for attempt in range(6):
            request = Request(url, data=data, headers=headers, method=method)
            try:
                with urlopen(request, timeout=self._request_timeout_seconds) as response:
                    raw = response.read()
                    body = json.loads(raw) if raw else None
                    return HttpResult(
                        status=response.status,
                        headers={key: value for key, value in response.headers.items()},
                        body=body,
                    )
            except HTTPError as exc:
                raw = exc.read()
                try:
                    body = json.loads(raw) if raw else None
                except json.JSONDecodeError:
                    body = None
                response_headers = {key: value for key, value in exc.headers.items()}
                if exc.code == 429 and attempt < 5:
                    self._sleep(_retry_after(response_headers))
                    continue
                raise FabricDeploymentError(
                    f"Fabric API {method} failed with HTTP {exc.code}: {_error_summary(body)}"
                ) from exc
            except URLError as exc:
                raise FabricDeploymentError(f"Fabric API {method} network failure") from exc
        raise FabricDeploymentError("Fabric API retry budget exhausted")

    @staticmethod
    def _require_status(result: HttpResult, expected: set[int], operation: str) -> None:
        if result.status not in expected:
            raise FabricDeploymentError(
                f"{operation} returned HTTP {result.status}: {_error_summary(result.body)}"
            )

    def _wait_operation(
        self,
        headers: Mapping[str, str],
        *,
        expect_result: bool,
    ) -> object | None:
        operation_id = _header(headers, "x-ms-operation-id")
        if operation_id is None:
            raise FabricDeploymentError("Fabric LRO response did not include x-ms-operation-id")
        operation_id = _uuid(operation_id, "Fabric operation id")
        deadline = self._monotonic() + self._lro_timeout_seconds
        delay = _retry_after(headers)

        while True:
            if self._monotonic() >= deadline:
                raise FabricDeploymentError("Fabric long-running operation timed out")
            self._sleep(delay)
            state = self._request("GET", f"operations/{operation_id}")
            self._require_status(state, {200}, "Fabric operation state")
            if not isinstance(state.body, Mapping):
                raise FabricDeploymentError("Fabric operation state response was not an object")
            status = state.body.get("status")
            if status == "Succeeded":
                if not expect_result:
                    return None
                result = self._request("GET", f"operations/{operation_id}/result")
                self._require_status(result, {200}, "Fabric operation result")
                return result.body
            if status == "Failed":
                raise FabricDeploymentError(
                    f"Fabric long-running operation failed: {_error_summary(state.body.get('error'))}"
                )
            if status not in {"NotStarted", "Running"}:
                raise FabricDeploymentError(f"Unsupported Fabric operation status: {status!r}")
            delay = _retry_after(state.headers)

    def list_items(self, workspace_id: str, item_type: str) -> list[Mapping[str, object]]:
        workspace = _uuid(workspace_id, "workspace_id")
        query = urlencode({"type": item_type})
        next_url: str | None = f"workspaces/{workspace}/items?{query}"
        items: list[Mapping[str, object]] = []
        visited: set[str] = set()

        while next_url is not None:
            absolute = self._absolute_url(next_url)
            if absolute in visited:
                raise FabricDeploymentError("Fabric item pagination repeated a continuation URL")
            visited.add(absolute)
            response = self._request("GET", absolute)
            self._require_status(response, {200}, "List Fabric items")
            if not isinstance(response.body, Mapping):
                raise FabricDeploymentError("List Fabric items response was not an object")
            values = response.body.get("value")
            if not isinstance(values, list):
                raise FabricDeploymentError("List Fabric items response did not contain a value list")
            for item in values:
                if isinstance(item, Mapping):
                    items.append(item)

            continuation_uri = response.body.get("continuationUri")
            continuation_token = response.body.get("continuationToken")
            if isinstance(continuation_uri, str) and continuation_uri:
                next_url = continuation_uri
            elif isinstance(continuation_token, str) and continuation_token:
                next_url = (
                    f"workspaces/{workspace}/items?"
                    + urlencode({"type": item_type, "continuationToken": continuation_token})
                )
            else:
                next_url = None
        return items

    def find_exact_item(
        self,
        workspace_id: str,
        *,
        item_type: str,
        display_name: str,
    ) -> Mapping[str, object] | None:
        matches = [
            item
            for item in self.list_items(workspace_id, item_type)
            if item.get("type") == item_type and item.get("displayName") == display_name
        ]
        if len(matches) > 1:
            raise FabricDeploymentError(
                f"Multiple {item_type} items have exact display name {display_name!r}; refusing to guess"
            )
        return matches[0] if matches else None

    def create_notebook(self, workspace_id: str, payload: Mapping[str, object]) -> Mapping[str, object]:
        workspace = _uuid(workspace_id, "workspace_id")
        response = self._request("POST", f"workspaces/{workspace}/notebooks", payload)
        self._require_status(response, {201, 202}, "Create Notebook")
        body = response.body if response.status == 201 else self._wait_operation(response.headers, expect_result=True)
        if not isinstance(body, Mapping):
            raise FabricDeploymentError("Create Notebook did not return an item object")
        return body

    def create_pipeline(self, workspace_id: str, payload: Mapping[str, object]) -> Mapping[str, object]:
        workspace = _uuid(workspace_id, "workspace_id")
        response = self._request("POST", f"workspaces/{workspace}/dataPipelines", payload)
        self._require_status(response, {201, 202}, "Create Data Pipeline")
        body = response.body if response.status == 201 else self._wait_operation(response.headers, expect_result=True)
        if not isinstance(body, Mapping):
            raise FabricDeploymentError("Create Data Pipeline did not return an item object")
        return body

    def update_notebook_definition(
        self,
        workspace_id: str,
        notebook_id: str,
        definition: Mapping[str, object],
    ) -> None:
        workspace = _uuid(workspace_id, "workspace_id")
        item_id = _uuid(notebook_id, "notebook_id")
        response = self._request(
            "POST",
            f"workspaces/{workspace}/notebooks/{item_id}/updateDefinition",
            {"definition": definition},
        )
        self._require_status(response, {200, 202}, "Update Notebook definition")
        if response.status == 202:
            self._wait_operation(response.headers, expect_result=False)

    def update_pipeline_definition(
        self,
        workspace_id: str,
        pipeline_id: str,
        definition: Mapping[str, object],
    ) -> None:
        workspace = _uuid(workspace_id, "workspace_id")
        item_id = _uuid(pipeline_id, "pipeline_id")
        response = self._request(
            "POST",
            f"workspaces/{workspace}/dataPipelines/{item_id}/updateDefinition",
            {"definition": definition},
        )
        self._require_status(response, {200, 202}, "Update Data Pipeline definition")
        if response.status == 202:
            self._wait_operation(response.headers, expect_result=False)


def _item_id(item: Mapping[str, object], label: str) -> str:
    raw = item.get("id")
    if not isinstance(raw, str):
        raise FabricDeploymentError(f"{label} response did not contain an item UUID")
    return _uuid(raw, f"{label} item id")


def deploy_certification_items(
    client: FabricApiClient,
    *,
    environment: str,
    workspace_id: str,
    key_vault_url: str | None = None,
    control_plane_secret_name: str | None = None,
    warehouse_secret_name: str | None = None,
    control_plane_server: str | None = None,
    control_plane_database: str | None = None,
    warehouse_server: str | None = None,
    warehouse_database: str | None = None,
    runtime_auth_mode: str = RUNTIME_AUTH_KEY_VAULT,
    notebook_display_name: str = DEFAULT_NOTEBOOK_NAME,
    pipeline_display_name: str = DEFAULT_PIPELINE_NAME,
    customer_inputs_root: str = DEFAULT_INPUTS_ROOT,
) -> dict[str, object]:
    if environment not in {"DEV", "UAT"}:
        raise FabricDeploymentError("certification Fabric item deployment is restricted to DEV/UAT")
    workspace = _uuid(workspace_id, "workspace_id")

    notebook_payload = render_notebook_payload(display_name=notebook_display_name)
    existing_notebook = client.find_exact_item(
        workspace,
        item_type="Notebook",
        display_name=notebook_display_name,
    )
    if existing_notebook is None:
        notebook = client.create_notebook(workspace, notebook_payload)
        notebook_action = "created"
    else:
        notebook = existing_notebook
        definition = notebook_payload.get("definition")
        if not isinstance(definition, Mapping):
            raise FabricDeploymentError("rendered Notebook definition was invalid")
        client.update_notebook_definition(workspace, _item_id(notebook, "Notebook"), definition)
        notebook_action = "updated"
    notebook_id = _item_id(notebook, "Notebook")

    pipeline_payload = render_pipeline_create_payload(
        display_name=pipeline_display_name,
        workspace_id=workspace,
        notebook_id=notebook_id,
        runtime_auth_mode=runtime_auth_mode,
        key_vault_url=key_vault_url,
        control_plane_secret_name=control_plane_secret_name,
        warehouse_secret_name=warehouse_secret_name,
        control_plane_server=control_plane_server,
        control_plane_database=control_plane_database,
        warehouse_server=warehouse_server,
        warehouse_database=warehouse_database,
        customer_inputs_root=customer_inputs_root,
    )
    existing_pipeline = client.find_exact_item(
        workspace,
        item_type="DataPipeline",
        display_name=pipeline_display_name,
    )
    if existing_pipeline is None:
        pipeline = client.create_pipeline(workspace, pipeline_payload)
        pipeline_action = "created"
    else:
        pipeline = existing_pipeline
        definition = pipeline_payload.get("definition")
        if not isinstance(definition, Mapping):
            raise FabricDeploymentError("rendered Data Pipeline definition was invalid")
        client.update_pipeline_definition(workspace, _item_id(pipeline, "Data Pipeline"), definition)
        pipeline_action = "updated"
    pipeline_id = _item_id(pipeline, "Data Pipeline")

    return {
        "schema_version": 1,
        "environment": environment,
        "workspace_id": workspace,
        "runtime_auth_mode": runtime_auth_mode,
        "notebook": {
            "id": notebook_id,
            "display_name": notebook_display_name,
            "action": notebook_action,
            "definition_sha256": _canonical_sha256(notebook_payload["definition"]),
        },
        "pipeline": {
            "id": pipeline_id,
            "display_name": pipeline_display_name,
            "action": pipeline_action,
            "definition_sha256": _canonical_sha256(pipeline_payload["definition"]),
        },
        "customer_inputs_root": customer_inputs_root,
        "contains_secret_values": False,
        "certification_result": "NOT_RUN",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Idempotently deploy the repository-owned Fabric certification Notebook/Pipeline."
    )
    parser.add_argument("--apply", action="store_true", help="Required explicit mutation authorization.")
    parser.add_argument("--environment", required=True, choices=("DEV", "UAT"))
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument(
        "--auth-mode",
        choices=(API_AUTH_AZURE_CLI, API_AUTH_ENV_TOKEN),
        default=API_AUTH_AZURE_CLI,
        help="Fabric REST API authentication. azure-cli uses the current az login session.",
    )
    parser.add_argument(
        "--runtime-auth-mode",
        choices=(RUNTIME_AUTH_FABRIC_USER, RUNTIME_AUTH_KEY_VAULT),
        default=RUNTIME_AUTH_FABRIC_USER,
        help="SQL runtime authentication inside the certification Notebook.",
    )
    parser.add_argument("--control-plane-server")
    parser.add_argument("--control-plane-database")
    parser.add_argument("--warehouse-server")
    parser.add_argument("--warehouse-database")
    parser.add_argument("--key-vault-url")
    parser.add_argument("--control-plane-secret-name")
    parser.add_argument("--warehouse-secret-name")
    parser.add_argument("--notebook-display-name", default=DEFAULT_NOTEBOOK_NAME)
    parser.add_argument("--pipeline-display-name", default=DEFAULT_PIPELINE_NAME)
    parser.add_argument("--customer-inputs-root", default=DEFAULT_INPUTS_ROOT)
    parser.add_argument("--access-token-env-var", default=DEFAULT_ACCESS_TOKEN_ENV_VAR)
    parser.add_argument("--lro-timeout-seconds", type=int, default=900)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/fabric-items/deployment-result.json"),
    )
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()
    if not args.apply:
        parser.error("--apply is required; deployment mutates the target Fabric workspace")
    if args.lro_timeout_seconds < 1:
        parser.error("--lro-timeout-seconds must be positive")

    try:
        if args.auth_mode == API_AUTH_AZURE_CLI:
            token = _azure_cli_access_token()
        else:
            token = os.environ.get(args.access_token_env_var, "").strip()
            if not token:
                raise FabricDeploymentError(
                    f"environment variable {args.access_token_env_var} must contain an approved Fabric API access token"
                )

        client = FabricApiClient(token, lro_timeout_seconds=args.lro_timeout_seconds)
        result = deploy_certification_items(
            client,
            environment=args.environment,
            workspace_id=args.workspace_id,
            runtime_auth_mode=args.runtime_auth_mode,
            key_vault_url=args.key_vault_url,
            control_plane_secret_name=args.control_plane_secret_name,
            warehouse_secret_name=args.warehouse_secret_name,
            control_plane_server=args.control_plane_server,
            control_plane_database=args.control_plane_database,
            warehouse_server=args.warehouse_server,
            warehouse_database=args.warehouse_database,
            notebook_display_name=args.notebook_display_name,
            pipeline_display_name=args.pipeline_display_name,
            customer_inputs_root=args.customer_inputs_root,
        )
    except (FabricDeploymentError, ValueError) as exc:
        parser.error(str(exc))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "workspace_id": result["workspace_id"],
                "runtime_auth_mode": result["runtime_auth_mode"],
                "notebook": result["notebook"],
                "pipeline": result["pipeline"],
                "certification_result": "NOT_RUN",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
