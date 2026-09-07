"""Initialize dedicated certification Warehouse and Fabric SQL Database resources.

Run only inside the isolated certification venv after the exact Framework wheel has
been verified and installed. Authentication uses the current Azure CLI user; tokens are
never printed or retained.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess

from fabric_data_framework.adapters.fabric.sql_auth import (
    CONTROL_PLANE_SQL_DATABASE_ENV_VAR,
    CONTROL_PLANE_SQL_SERVER_ENV_VAR,
    FABRIC_SQL_AUTH_MODE_ENV_VAR,
    FABRIC_SQL_AUTH_MODE_USER,
    WAREHOUSE_SQL_DATABASE_ENV_VAR,
    WAREHOUSE_SQL_SERVER_ENV_VAR,
    create_runtime_sql_engine,
)
from fabric_data_framework.control_plane.schema import apply_baseline_schema
from fabric_data_framework.deployment.delivery import (
    load_dataset_configs,
    materialize_semantic_metadata,
)


SQL_TOKEN_AUDIENCE = "https://database.windows.net/"


def _token(audience: str) -> str:
    try:
        completed = subprocess.run(
            [
                "az",
                "account",
                "get-access-token",
                "--resource",
                audience,
                "--query",
                "accessToken",
                "-o",
                "tsv",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("Azure CLI is required for certification SQL bootstrap") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "Azure CLI could not obtain the Fabric SQL token; run az login first"
        ) from exc
    value = completed.stdout.strip()
    if not value or "\n" in value or "\r" in value:
        raise RuntimeError("Azure CLI returned an empty or malformed SQL token")
    return value


def _token_getter(audience: str) -> str:
    if audience != SQL_TOKEN_AUDIENCE:
        raise RuntimeError("unexpected SQL token audience requested")
    return _token(audience)


def _engine(role: str, *, server: str, database: str):
    if role == "control-plane":
        server_env = CONTROL_PLANE_SQL_SERVER_ENV_VAR
        database_env = CONTROL_PLANE_SQL_DATABASE_ENV_VAR
    elif role == "warehouse":
        server_env = WAREHOUSE_SQL_SERVER_ENV_VAR
        database_env = WAREHOUSE_SQL_DATABASE_ENV_VAR
    else:
        raise ValueError(f"unsupported SQL bootstrap role: {role}")
    environ = {
        FABRIC_SQL_AUTH_MODE_ENV_VAR: FABRIC_SQL_AUTH_MODE_USER,
        server_env: server,
        database_env: database,
    }
    return create_runtime_sql_engine(
        role=role,  # type: ignore[arg-type]
        environ=environ,
        database_url_env_var=None,
        token_getter=_token_getter,
    )


def _execute_sql_file(engine, path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    batches = [part.strip() for part in re.split(r"(?im)^\s*GO\s*$", sql) if part.strip()]
    with engine.begin() as connection:
        for batch in batches:
            connection.exec_driver_sql(batch)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--control-plane-server", required=True)
    parser.add_argument("--control-plane-database", required=True)
    parser.add_argument("--warehouse-server", required=True)
    parser.add_argument("--warehouse-database", required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--warehouse-fixtures", type=Path, required=True)
    parser.add_argument("--customer-git-sha", required=True)
    parser.add_argument("--framework-version", required=True)
    parser.add_argument("--apply-warehouse-fixtures", action="store_true")
    parser.add_argument("--apply-control-plane-schema", action="store_true")
    parser.add_argument("--materialize-control-plane-metadata", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.materialize_control_plane_metadata and not args.apply_control_plane_schema:
        raise ValueError("metadata materialization requires Control Plane schema bootstrap")

    result: dict[str, object] = {
        "contains_secret_values": False,
        "warehouse_fixtures": "NOT_REQUESTED",
        "control_plane_schema": "NOT_REQUESTED",
        "control_plane_metadata": "NOT_REQUESTED",
    }

    if args.apply_warehouse_fixtures:
        if not args.warehouse_fixtures.is_file():
            raise ValueError(f"Warehouse fixture SQL is missing: {args.warehouse_fixtures}")
        engine = _engine(
            "warehouse",
            server=args.warehouse_server,
            database=args.warehouse_database,
        )
        try:
            _execute_sql_file(engine, args.warehouse_fixtures)
        finally:
            engine.dispose()
        result["warehouse_fixtures"] = "APPLIED"

    if args.apply_control_plane_schema:
        engine = _engine(
            "control-plane",
            server=args.control_plane_server,
            database=args.control_plane_database,
        )
        try:
            apply_baseline_schema(engine)
            result["control_plane_schema"] = "APPLIED"
            if args.materialize_control_plane_metadata:
                configs = load_dataset_configs(args.project_root / "config/datasets")
                bundle_hash = materialize_semantic_metadata(
                    engine,
                    configs=configs,
                    domain="customer-certification",
                    domain_git_sha=args.customer_git_sha,
                    framework_version=args.framework_version,
                )
                result["control_plane_metadata"] = "MATERIALIZED"
                result["config_bundle_hash"] = bundle_hash
                result["dataset_count"] = len(configs)
        finally:
            engine.dispose()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
