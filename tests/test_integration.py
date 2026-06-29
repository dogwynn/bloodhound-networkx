import networkx as nx
from bloodhound_networkx import networkx as bnx
from bloodhound_networkx import analysis

def test_directory_parsing_integration(parsed_bloodhound_data):
    """Verifies that the entire directory correctly streams dictionaries."""
    assert len(parsed_bloodhound_data) > 0, "Should have parsed entities"
    
    # Ensure types were injected and properties exist
    first_entity = parsed_bloodhound_data[0]
    assert "type" in first_entity
    assert "Properties" in first_entity

def test_graph_creation_integration(sample_graph):
    """Verifies the integration between the parsed dicts and NetworkX graphing."""
    assert isinstance(sample_graph, nx.MultiDiGraph)
    
    # Metadata node injected by networkx.py should exist
    assert "__metadata__" in sample_graph.nodes
    assert "hash" in sample_graph.nodes["__metadata__"]
    
    # Must have populated nodes and edges
    assert len(sample_graph.nodes) > 1
    assert len(sample_graph.edges) > 0

def test_analysis_methods(sample_graph):
    """Integration test checking that analysis functions can query the graph."""
    # Test retrieving users
    users = analysis.all_users(sample_graph)
    assert isinstance(users, tuple)
    
    # Test retrieving groups
    groups = analysis.all_groups(sample_graph)
    assert isinstance(groups, tuple)
    
    # Ensure properties exist on fetched nodes
    if len(users) > 0:
        assert "name" in users[0]

def test_graph_persistence(sample_graph, tmp_path):
    """Tests the pickling and unpickling of the parsed graph."""
    bnx.pickle_graph(tmp_path, "test_stem", sample_graph)
    pkl_file = bnx.pickle_path(tmp_path, "test_stem")
    
    assert pkl_file.exists(), "Pickle/GZ file should be created"
    
    unpickled_G = bnx.unpickle_graph(pkl_file)
    assert isinstance(unpickled_G, nx.MultiDiGraph)
    assert len(unpickled_G.nodes) == len(sample_graph.nodes)