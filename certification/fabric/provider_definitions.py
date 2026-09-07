"""Repository-owned Fabric Copy/Spark definitions used by certification bootstrap.

Definitions contain only non-secret physical item identity. They prepare real provider
items; they do not execute certification and do not author PASS evidence.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path
from uuid import UUID, uuid5


ROOT = Path(__file__).resolve().parent
SPARK_ROOT = ROOT / "spark"
_COPY_ACTIVITY_NAMESPACE = UUID("2670c402-3c47-4da5-8564-3aa418e30a85")


def _uuid(value: str, label: str) -> str:
    try:
        return str(UUID(value))
    except ValueError as exc:
        raise ValueError(f"{label} must be a UUID") from exc


def _b64_bytes(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _b64_json(value: object) -> str:
    return _b64_bytes((json.dumps(value, indent=2) + "\n").encode("utf-8"))


def copy_job_payload(
    *,
    display_name: str,
    workspace_id: str,
    lakehouse_id: str,
) -> dict[str, object]:
    workspace = _uuid(workspace_id, "workspace_id")
    lakehouse = _uuid(lakehouse_id, "lakehouse_id")
    activity_id = str(uuid5(_COPY_ACTIVITY_NAMESPACE, f"{workspace}:{lakehouse}:cert.copy"))
    connection = {
        "type": "LakehouseTable",
        "connectionSettings": {
            "type": "Lakehouse",
            "typeProperties": {
                "workspaceId": workspace,
                "artifactId": lakehouse,
                "rootFolder": "Tables",
            },
        },
    }
    content = {
        "properties": {
            "jobMode": "Batch",
            "source": connection,
            "destination": connection,
            "policy": {"timeout": "0.01:00:00", "retry": 0},
        },
        "activities": [
            {
                "id": activity_id,
                "properties": {
                    "source": {
                        "datasetSettings": {
                            "schema": "dbo",
                            "table": "cert_copy_source",
                        },
                        "partitionSettings": {"partitionOption": "None"},
                    },
                    "destination": {
                        "datasetSettings": {
                            "schema": "dbo",
                            "table": "cert_copy_landing",
                        },
                        "writeBehavior": "Overwrite",
                        "tableOption": "autoCreate",
                    },
                    "enableStaging": False,
                    "translator": {"type": "TabularTranslator"},
                    "typeConversionSettings": {
                        "typeConversion": {
                            "allowDataTruncation": False,
                            "treatBooleanAsNumber": False,
                        }
                    },
                },
            }
        ],
    }
    return {
        "displayName": display_name,
        "type": "CopyJob",
        "description": "Repository-owned bounded certification Copy Job.",
        "definition": {
            "parts": [
                {
                    "path": "copyjob-content.json",
                    "payload": _b64_json(content),
                    "payloadType": "InlineBase64",
                }
            ]
        },
    }


def spark_job_payload(
    *,
    display_name: str,
    workspace_id: str,
    lakehouse_id: str,
    script_path: str | Path,
    description: str,
) -> dict[str, object]:
    _uuid(workspace_id, "workspace_id")
    lakehouse = _uuid(lakehouse_id, "lakehouse_id")
    script = Path(script_path)
    if not script.is_file() or script.suffix != ".py":
        raise ValueError(f"Spark main script must be an existing .py file: {script}")
    definition = {
        "executableFile": "main.py",
        "language": "Python",
        "mainClass": "",
        "defaultLakehouseArtifactId": lakehouse,
        "additionalLakehouseIds": [],
        "commandLineArguments": "",
        "additionalLibraryUris": [],
    }
    return {
        "displayName": display_name,
        "type": "SparkJobDefinition",
        "description": description,
        "definition": {
            "format": "SparkJobDefinitionV2",
            "parts": [
                {
                    "path": "SparkJobDefinitionV1.json",
                    "payload": _b64_json(definition),
                    "payloadType": "InlineBase64",
                },
                {
                    "path": "Main/main.py",
                    "payload": _b64_bytes(script.read_bytes()),
                    "payloadType": "InlineBase64",
                },
            ],
        },
    }


def seed_spark_job_payload(
    *,
    display_name: str,
    workspace_id: str,
    lakehouse_id: str,
) -> dict[str, object]:
    return spark_job_payload(
        display_name=display_name,
        workspace_id=workspace_id,
        lakehouse_id=lakehouse_id,
        script_path=SPARK_ROOT / "seed.py",
        description="Setup-only certification source-table seed; never certification evidence.",
    )


def capture_spark_job_payload(
    *,
    display_name: str,
    workspace_id: str,
    lakehouse_id: str,
) -> dict[str, object]:
    return spark_job_payload(
        display_name=display_name,
        workspace_id=workspace_id,
        lakehouse_id=lakehouse_id,
        script_path=SPARK_ROOT / "capture.py",
        description="Repository-owned bounded Spark capture used by Framework evidence runner.",
    )


__all__ = [
    "capture_spark_job_payload",
    "copy_job_payload",
    "seed_spark_job_payload",
    "spark_job_payload",
]
