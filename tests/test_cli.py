import pytest
from click.testing import CliRunner
from pathlib import Path

# Important: Import process to ensure commands are bound to bnx_cli
import bloodhound_networkx.cli.process 
from bloodhound_networkx.cli.common import bnx_cli

@pytest.fixture
def cli_runner():
    return CliRunner()

def test_cli_process_command(cli_runner, sample_data_dir, tmp_path):
    """Tests compiling JSON files into a cached pickle graph."""
    result = cli_runner.invoke(bnx_cli, [
        "process", 
        str(sample_data_dir), 
        "--output-dir", str(tmp_path), 
        "-o", "cli_test_graph"
    ])
    
    assert result.exit_code == 0
    assert (tmp_path / "cli_test_graph.pkl.gz").exists()

def test_cli_list_users_from_json(cli_runner, sample_data_dir):
    """Tests the list-users command processing directly from JSON dir."""
    result = cli_runner.invoke(bnx_cli, [
        "list-users", 
        str(sample_data_dir),
        "-c", "name", 
        "-c", "enabled"
    ])
    
    assert result.exit_code == 0
    assert result.output != ""

def test_cli_list_groups_column_counts(cli_runner, sample_data_dir):
    """Tests the --column-counts flag for groups."""
    result = cli_runner.invoke(bnx_cli, [
        "list-groups", 
        str(sample_data_dir),
        "--column-counts"
    ])
    
    assert result.exit_code == 0
    # Output should contain standard column keys like "name" or "type" count format
    assert ":" in result.output