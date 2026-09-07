import ast
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_PACKAGE = "fabric_data_framework"
FRAMEWORK_DISTRIBUTION = "fabric-data-framework"


def _imports_framework(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) and any(
            alias.name == FRAMEWORK_PACKAGE
            or alias.name.startswith(f"{FRAMEWORK_PACKAGE}.")
            for alias in node.names
        ):
            return True
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == FRAMEWORK_PACKAGE or module.startswith(f"{FRAMEWORK_PACKAGE}."):
                return True
    return False


def test_production_python_does_not_import_framework():
    offenders = [
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "src").rglob("*.py")
        if _imports_framework(path)
    ]
    assert offenders == []


def test_project_has_no_framework_dependency_in_any_dependency_group():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    dependency_groups = [project.get("dependencies", [])]
    dependency_groups.extend(project.get("optional-dependencies", {}).values())

    dependencies = [dependency.lower() for group in dependency_groups for dependency in group]
    assert not any(FRAMEWORK_DISTRIBUTION in dependency for dependency in dependencies)
