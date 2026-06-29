import pytest
from pathlib import Path

import networkx as nx
from bloodhound_networkx.toolz import *
from bloodhound_networkx import bloodhound
from bloodhound_networkx import networkx as bnx

@pytest.fixture(scope="session")
def sample_data_dir() -> Path:
    """Fixture to resolve the sample data directory."""
    # Attempt paths based on execution context
    return Path("tests/data/ad_sampledata/20240305110018/")
    

@pytest.fixture(scope="session")
def sample_json_files(sample_data_dir) -> list[Path]:
    """Returns a list of all JSON files in the sample directory."""
    return list(sample_data_dir.glob("*.json"))

@pytest.fixture(scope="session")
def parsed_bloodhound_data(sample_data_dir):
    """Fixture that parses the directory once for use in integration tests."""
    return tuple(bloodhound.parse_directory(sample_data_dir))

@pytest.fixture(scope="session")
def sample_graph(parsed_bloodhound_data) -> nx.MultiDiGraph:
    """Fixture that generates a full MultiDiGraph from the parsed data."""
    return bnx.to_digraph(parsed_bloodhound_data)

@pytest.fixture(scope="session")
def bh_objects(sample_data_dir) -> dict:
    return pipe(
        sample_data_dir.glob('*.json'),
        sorted,
        map(json_slurp),
        mapcat(lambda json: pipe(
            json['data'], 
            map(lambda d: merge(d, {'type': json['meta']['type']})),
        )),
        groupby('type'),
        valmap(sort_by(lambda d: d['Properties']['name'])),
        valmap(last),
    )

@pytest.fixture(scope="session")
def bh_object_edge_counts() -> dict:
    return {
        'aiacas': 11, 'certtemplates': 10, 'computers': 11, 
        'containers': 5, 'domains': 27, 'enterprisecas': 16, 
        'gpos': 8, 'groups': 6, 'ntauthstores': 9, 'ous': 8, 
        'rootcas': 11, 'users': 12
    }