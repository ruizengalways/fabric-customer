"""Render credential-free Fabric Notebook/DataPipeline create payloads for certification.

The renderer intentionally accepts only non-secret deployment bindings.  Actual SQL
connection strings are resolved by the worker Notebook from Key Vault at runtime.
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
_SAFE_SECRET_NAME = re.compile(r"^[A-Za-z0-9-]{1,127}$")


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


def render_pipeline_content(
    *,
    workspace_id: str,
    notebook_id: str,
    key_vault_url: str,
    control_plane_secret_name: str,
    warehouse_secret_name: str,
    customer_inputs_root: str = DEFAULT_INPUTS_ROOT,
) -> dict[str, object]:
    replacements = {
        "__WORKSPACE_ID__": _uuid(workspace_id, "workspace_id"),
        "__NOTEBOOK_ID__": _uuid(notebook_id, "notebook_id"),
        "__KEY_VAULT_URL__": _key_vault_url(key_vault_url),
        "__CONTROL_PLANE_SECRET_NAME__": _secret_name(
            control_plane_secret_name, "control_plane_secret_name"
        ),
        "__WAREHOUSE_SECRET_NAME__": _secret_name(
            warehouse_secret_name, "warehouse_secret_name"
        ),
        "__CUSTOMER_INPUTS_ROOT__": _inputs_root(customer_inputs_root),
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
    key_vault_url: str,
    control_plane_secret_name: str,
    warehouse_secret_name: str,
    customer_inputs_root: str = DEFAULT_INPUTS_ROOT,
) -> dict[str, object]:
    content = render_pipeline_content(
        workspace_id=workspace_id,
        notebook_id=notebook_id,
        key_vault_url=key_vault_url,
        control_plane_secret_name=control_plane_secret_name,
        warehouse_secret_name=warehouse_secret_name,
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
    pipeline.add_argument("--key-vault-url", required=True)
    pipeline.add_argument("--control-plane-secret-name", required=True)
    pipeline.add_argument("--warehouse-secret-name", required=True)
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
            key_vault_url=args.key_vault_url,
            control_plane_secret_name=args.control_plane_secret_name,
            warehouse_secret_name=args.warehouse_secret_name,
            customer_inputs_root=args.customer_inputs_root,
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
