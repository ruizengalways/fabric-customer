"""Render credential-free Fabric Notebook/DataPipeline create payloads for certification.

Fabric-native user authentication is the preferred deployment/runtime lane.  The
existing Key Vault lane remains available for organizations that intentionally manage
runtime SQL URLs as secrets.  No bearer token, database password or secret value is
accepted by this renderer.
"""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
import re
from urllib.parse import urlparse
from uuid import UUID


ROOT = Path(__file__).resolve().parent
NOTEBOOK_TEMPLATE = ROOT / "notebook" / "certification-pipeline-worker.ipynb"
PIPELINE_TEMPLATE = ROOT / "pipeline" / "pipeline-content.template.json"
DEFAULT_INPUTS_ROOT = "/lakehouse/default/Files/framework_cert/customer-inputs"
RUNTIME_AUTH_FABRIC_USER = "fabric-user"
RUNTIME_AUTH_KEY_VAULT = "key-vault"
_SAFE_SECRET_NAME = re.compile(r"^[A-Za-z0-9-]{1,127}$")
_SAFE_SERVER = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9.-]{0,253}[A-Za-z0-9])?(?:(?:,|:)1433)?$")


def _uuid(value: str, label: str) -> str:
    try:
        return str(UUID(value))
    except ValueError as exc:
        raise ValueError(f"{label} must be a UUID") from exc


def _key_vault_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError("key_vault_url must be a credential-free HTTPS URL")
    if parsed.query or parsed.fragment:
        raise ValueError("key_vault_url must not contain query/fragment material")
    return value.rstrip("/")


def _secret_name(value: str, label: str) -> str:
    if _SAFE_SECRET_NAME.fullmatch(value) is None:
        raise ValueError(f"{label} must be a Key Vault secret name, not a secret value")
    return value


def _sql_server(value: str, label: str) -> str:
    candidate = value.strip()
    if _SAFE_SERVER.fullmatch(candidate) is None:
        raise ValueError(f"{label} must be a plain Fabric SQL hostname with optional port 1433")
    if candidate.endswith(",1433") or candidate.endswith(":1433"):
        candidate = candidate[:-5]
    return candidate


def _database_name(value: str, label: str) -> str:
    candidate = value.strip()
    if not candidate or len(candidate) > 256:
        raise ValueError(f"{label} must contain 1-256 characters")
    if any(char in candidate for char in (";", "\r", "\n", "\x00", "{", "}")):
        raise ValueError(f"{label} contains unsafe connection-string characters")
    return candidate


def _inputs_root(value: str) -> str:
    if value != DEFAULT_INPUTS_ROOT:
        raise ValueError(
            "certification customer_inputs_root must use the conventional attached-Lakehouse path"
        )
    return value


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def render_notebook_payload(*, display_name: str) -> dict[str, object]:
    content = NOTEBOOK_TEMPLATE.read_bytes()
    json.loads(content)
    return {
        "displayName": display_name,
        "description": "Exact Framework certification child worker; credentials resolve at runtime.",
        "definition": {
            "format": "ipynb",
            "parts": [
                {
                    "path": "notebook-content.ipynb",
                    "payload": _b64(content),
                    "payloadType": "InlineBase64",
                }
            ],
        },
    }


def _runtime_replacements(
    *,
    runtime_auth_mode: str,
    key_vault_url: str | None,
    control_plane_secret_name: str | None,
    warehouse_secret_name: str | None,
    control_plane_server: str | None,
    control_plane_database: str | None,
    warehouse_server: str | None,
    warehouse_database: str | None,
) -> dict[str, str]:
    if runtime_auth_mode == RUNTIME_AUTH_FABRIC_USER:
        required = {
            "control_plane_server": control_plane_server,
            "control_plane_database": control_plane_database,
            "warehouse_server": warehouse_server,
            "warehouse_database": warehouse_database,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError("fabric-user runtime requires " + ", ".join(missing))
        return {
            "__RUNTIME_AUTH_MODE__": RUNTIME_AUTH_FABRIC_USER,
            "__KEY_VAULT_URL__": "",
            "__CONTROL_PLANE_SECRET_NAME__": "",
            "__WAREHOUSE_SECRET_NAME__": "",
            "__CONTROL_PLANE_SERVER__": _sql_server(control_plane_server or "", "control_plane_server"),
            "__CONTROL_PLANE_DATABASE__": _database_name(
                control_plane_database or "", "control_plane_database"
            ),
            "__WAREHOUSE_SERVER__": _sql_server(warehouse_server or "", "warehouse_server"),
            "__WAREHOUSE_DATABASE__": _database_name(
                warehouse_database or "", "warehouse_database"
            ),
        }
    if runtime_auth_mode == RUNTIME_AUTH_KEY_VAULT:
        required = {
            "key_vault_url": key_vault_url,
            "control_plane_secret_name": control_plane_secret_name,
            "warehouse_secret_name": warehouse_secret_name,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError("key-vault runtime requires " + ", ".join(missing))
        return {
            "__RUNTIME_AUTH_MODE__": RUNTIME_AUTH_KEY_VAULT,
            "__KEY_VAULT_URL__": _key_vault_url(key_vault_url or ""),
            "__CONTROL_PLANE_SECRET_NAME__": _secret_name(
                control_plane_secret_name or "", "control_plane_secret_name"
            ),
            "__WAREHOUSE_SECRET_NAME__": _secret_name(
                warehouse_secret_name or "", "warehouse_secret_name"
            ),
            "__CONTROL_PLANE_SERVER__": "",
            "__CONTROL_PLANE_DATABASE__": "",
            "__WAREHOUSE_SERVER__": "",
            "__WAREHOUSE_DATABASE__": "",
        }
    raise ValueError("runtime_auth_mode must be fabric-user or key-vault")


def render_pipeline_content(
    *,
    workspace_id: str,
    notebook_id: str,
    key_vault_url: str | None = None,
    control_plane_secret_name: str | None = None,
    warehouse_secret_name: str | None = None,
    control_plane_server: str | None = None,
    control_plane_database: str | None = None,
    warehouse_server: str | None = None,
    warehouse_database: str | None = None,
    runtime_auth_mode: str = RUNTIME_AUTH_KEY_VAULT,
    customer_inputs_root: str = DEFAULT_INPUTS_ROOT,
) -> dict[str, object]:
    replacements = {
        "__WORKSPACE_ID__": _uuid(workspace_id, "workspace_id"),
        "__NOTEBOOK_ID__": _uuid(notebook_id, "notebook_id"),
        "__CUSTOMER_INPUTS_ROOT__": _inputs_root(customer_inputs_root),
        **_runtime_replacements(
            runtime_auth_mode=runtime_auth_mode,
            key_vault_url=key_vault_url,
            control_plane_secret_name=control_plane_secret_name,
            warehouse_secret_name=warehouse_secret_name,
            control_plane_server=control_plane_server,
            control_plane_database=control_plane_database,
            warehouse_server=warehouse_server,
            warehouse_database=warehouse_database,
        ),
    }
    raw = PIPELINE_TEMPLATE.read_text(encoding="utf-8")
    for source, target in replacements.items():
        raw = raw.replace(source, target)
    if "__" in raw:
        raise ValueError("unresolved certification Pipeline template placeholder")
    return json.loads(raw)


def render_pipeline_create_payload(
    *,
    display_name: str,
    workspace_id: str,
    notebook_id: str,
    key_vault_url: str | None = None,
    control_plane_secret_name: str | None = None,
    warehouse_secret_name: str | None = None,
    control_plane_server: str | None = None,
    control_plane_database: str | None = None,
    warehouse_server: str | None = None,
    warehouse_database: str | None = None,
    runtime_auth_mode: str = RUNTIME_AUTH_KEY_VAULT,
    customer_inputs_root: str = DEFAULT_INPUTS_ROOT,
) -> dict[str, object]:
    content = render_pipeline_content(
        workspace_id=workspace_id,
        notebook_id=notebook_id,
        key_vault_url=key_vault_url,
        control_plane_secret_name=control_plane_secret_name,
        warehouse_secret_name=warehouse_secret_name,
        control_plane_server=control_plane_server,
        control_plane_database=control_plane_database,
        warehouse_server=warehouse_server,
        warehouse_database=warehouse_database,
        runtime_auth_mode=runtime_auth_mode,
        customer_inputs_root=customer_inputs_root,
    )
    encoded = _b64((json.dumps(content, indent=2) + "\n").encode("utf-8"))
    return {
        "displayName": display_name,
        "definition": {
            "parts": [
                {
                    "path": "pipeline-content.json",
                    "payload": encoded,
                    "payloadType": "InlineBase64",
                }
            ]
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    notebook = sub.add_parser("notebook")
    notebook.add_argument("--display-name", default="framework-certification-worker")
    notebook.add_argument("--output", type=Path, required=True)

    pipeline = sub.add_parser("pipeline")
    pipeline.add_argument("--display-name", default="framework-certification-child")
    pipeline.add_argument("--workspace-id", required=True)
    pipeline.add_argument("--notebook-id", required=True)
    pipeline.add_argument(
        "--runtime-auth-mode",
        choices=(RUNTIME_AUTH_FABRIC_USER, RUNTIME_AUTH_KEY_VAULT),
        default=RUNTIME_AUTH_FABRIC_USER,
    )
    pipeline.add_argument("--control-plane-server")
    pipeline.add_argument("--control-plane-database")
    pipeline.add_argument("--warehouse-server")
    pipeline.add_argument("--warehouse-database")
    pipeline.add_argument("--key-vault-url")
    pipeline.add_argument("--control-plane-secret-name")
    pipeline.add_argument("--warehouse-secret-name")
    pipeline.add_argument("--customer-inputs-root", default=DEFAULT_INPUTS_ROOT)
    pipeline.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "notebook":
        payload = render_notebook_payload(display_name=args.display_name)
    else:
        payload = render_pipeline_create_payload(
            display_name=args.display_name,
            workspace_id=args.workspace_id,
            notebook_id=args.notebook_id,
            runtime_auth_mode=args.runtime_auth_mode,
            key_vault_url=args.key_vault_url,
            control_plane_secret_name=args.control_plane_secret_name,
            warehouse_secret_name=args.warehouse_secret_name,
            control_plane_server=args.control_plane_server,
            control_plane_database=args.control_plane_database,
            warehouse_server=args.warehouse_server,
            warehouse_database=args.warehouse_database,
            customer_inputs_root=args.customer_inputs_root,
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
