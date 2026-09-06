from __future__ import annotations

import base64
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
FABRIC_ITEMS = ROOT / "certification/fabric_items"
WORKSPACE_ID = "00000000-0000-0000-0000-000000000001"
NOTEBOOK_ID = "00000000-0000-0000-0000-000000000002"
PIPELINE_ID = "00000000-0000-0000-0000-000000000003"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    sys.path.insert(0, str(FABRIC_ITEMS))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(FABRIC_ITEMS))
    return module


def _renderer():
    return _load_module("fabric_native_renderer", FABRIC_ITEMS / "render_fabric_items.py")


def _deployer():
    return _load_module("fabric_native_deployer", FABRIC_ITEMS / "deploy_fabric_items.py")


def _decode(payload):
    part = payload["definition"]["parts"][0]
    return json.loads(base64.b64decode(part["payload"]).decode("utf-8"))


def test_cli_defaults_to_current_azure_cli_user_and_fabric_user_runtime():
    module = _deployer()
    args = module._parser().parse_args(
        ["--apply", "--environment", "DEV", "--workspace-id", WORKSPACE_ID]
    )
    assert args.auth_mode == "azure-cli"
    assert args.runtime_auth_mode == "fabric-user"
    assert args.key_vault_url is None
    assert args.control_plane_secret_name is None
    assert args.warehouse_secret_name is None


def test_fabric_user_renderer_carries_only_non_secret_sql_identity():
    module = _renderer()
    content = module.render_pipeline_content(
        workspace_id=WORKSPACE_ID,
        notebook_id=NOTEBOOK_ID,
        runtime_auth_mode="fabric-user",
        control_plane_server="cp.database.fabric.microsoft.com",
        control_plane_database="framework_control",
        warehouse_server="wh.datawarehouse.fabric.microsoft.com",
        warehouse_database="framework_cert",
    )
    rendered = json.dumps(content)
    assert '"runtime_auth_mode"' in rendered
    assert "fabric-user" in rendered
    assert "cp.database.fabric.microsoft.com" in rendered
    assert "framework_control" in rendered
    assert "wh.datawarehouse.fabric.microsoft.com" in rendered
    assert "framework_cert" in rendered
    assert "vault.azure.net" not in rendered
    assert "__" not in rendered


def test_fabric_user_deploy_path_binds_real_notebook_id_without_key_vault():
    module = _deployer()

    class FakeClient:
        def find_exact_item(self, workspace_id, *, item_type, display_name):
            return None

        def create_notebook(self, workspace_id, payload):
            return {"id": NOTEBOOK_ID, "type": "Notebook", "displayName": payload["displayName"]}

        def create_pipeline(self, workspace_id, payload):
            self.pipeline_payload = payload
            return {"id": PIPELINE_ID, "type": "DataPipeline", "displayName": payload["displayName"]}

        def update_notebook_definition(self, *args, **kwargs):
            raise AssertionError("unexpected update")

        def update_pipeline_definition(self, *args, **kwargs):
            raise AssertionError("unexpected update")

    client = FakeClient()
    result = module.deploy_certification_items(
        client,
        environment="DEV",
        workspace_id=WORKSPACE_ID,
        runtime_auth_mode="fabric-user",
        control_plane_server="cp.database.fabric.microsoft.com",
        control_plane_database="framework_control",
        warehouse_server="wh.datawarehouse.fabric.microsoft.com",
        warehouse_database="framework_cert",
    )
    assert result["runtime_auth_mode"] == "fabric-user"
    assert result["contains_secret_values"] is False
    assert result["certification_result"] == "NOT_RUN"
    assert "key_vault" not in json.dumps(result).lower()
    content = _decode(client.pipeline_payload)
    params = content["properties"]["activities"][0]["typeProperties"]["parameters"]
    assert params["runtime_auth_mode"]["value"] == "fabric-user"
    assert params["control_plane_server"]["value"] == "cp.database.fabric.microsoft.com"
    assert params["key_vault_url"]["value"] == ""


def test_azure_cli_token_is_captured_not_printed(monkeypatch):
    module = _deployer()
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="opaque-token\n", stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    assert module._azure_cli_access_token() == "opaque-token"
    command, kwargs = calls[0]
    assert command[:3] == ["az", "account", "get-access-token"]
    assert "https://api.fabric.microsoft.com" in command
    assert kwargs["capture_output"] is True
    assert kwargs["text"] is True


def test_worker_supports_both_fabric_user_and_key_vault_without_embedding_credentials():
    notebook = json.loads(
        (FABRIC_ITEMS / "notebook/certification-pipeline-worker.ipynb").read_text()
    )
    source = "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
    )
    assert "prepare_fabric_user_sql_runtime" in source
    assert 'runtime_auth_mode == "fabric-user"' in source
    assert 'runtime_auth_mode == "key-vault"' in source
    assert "credentials.getSecret" in source
    assert "https://database.windows.net" not in source
    assert "opaque-token" not in source
