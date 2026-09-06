from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_candidate_input_workflow_exposes_only_canonical_enterprise_profile():
    workflow = (ROOT / ".github/workflows/candidate-business-path-inputs.yml").read_text(
        encoding="utf-8"
    )
    assert 'default: fabric_sql_database_v1' in workflow
    assert 'options: [fabric_sql_database_v1]' in workflow
    assert 'azure_sql_database_v1' not in workflow


def test_candidate_input_builder_fails_closed_on_enterprise_profile_drift():
    source = (ROOT / "certification/build_candidate_inputs.py").read_text(encoding="utf-8")
    assert "ENTERPRISE_FABRIC_CONTROL_PLANE_PROFILE_NAME" in source
    assert "assert_enterprise_fabric_control_plane_profile(args.control_plane_profile)" in source
    assert 'choices=(ENTERPRISE_FABRIC_CONTROL_PLANE_PROFILE_NAME,)' in source
    assert 'azure_sql_database_v1' not in source
