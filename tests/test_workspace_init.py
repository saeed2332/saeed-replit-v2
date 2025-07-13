def test_workspace_scaffolds_project(tmp_path):
    from saeed_replit import init_project
    init_project(tmp_path)
    assert (tmp_path / "README.md").exists()
