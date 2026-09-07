from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
IMPORT_PATTERN = re.compile(r"(?m)^\s*(?:from\s+fabric_data_framework\b|import\s+fabric_data_framework\b)")


def test_production_python_does_not_import_framework():
    offenders = []
    for path in (ROOT / "src").rglob("*.py"):
        if IMPORT_PATTERN.search(path.read_text(encoding="utf-8")):
            offenders.append(path.relative_to(ROOT).as_posix())
    assert offenders == []


def test_project_has_no_framework_runtime_dependency():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    project_section = pyproject.split("[project.optional-dependencies]", 1)[0]
    assert "fabric-data-framework" not in project_section.lower()
