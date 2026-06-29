import networkx as nx
from bloodhound_networkx.toolz import *
from bloodhound_networkx import bloodhound

def test_check_version_supported():
    """Unit test for version checking valid version."""
    data = {"meta": {"version": 6}}
    assert bloodhound.check_version(data) is True

def test_check_version_unsupported():
    """Unit test for version checking invalid/unsupported version."""
    data = {"meta": {"version": 5}}
    assert bloodhound.check_version(data) is False
    
    malformed_data = {"data": []}
    assert bloodhound.check_version(malformed_data) is False

def test_object_type_mapping():
    """Unit test for Bloodhound object type mapping."""
    assert bloodhound.object_type({"type": "users"}) == "User"
    assert bloodhound.object_type({"type": "computers"}) == "Computer"
    assert bloodhound.object_type({"type": "unknown_type"}) == "Base"

def test_object_properties_merging():
    """Unit test for properties creation."""
    obj = {
        "type": "groups",
        "ObjectIdentifier": "S-1-5-21-1234-5678",
        "Properties": {"name": "DOMAIN ADMINS"}
    }
    props = bloodhound.object_properties(obj)
    
    assert props["type"] == "Group"
    assert props["sid"] == "S-1-5-21-1234-5678"
    assert props["name"] == "DOMAIN ADMINS"

def test_object_edge_counts(bh_objects, bh_object_edge_counts):
    for otype, obj in bh_objects.items():
        edge_dicts = pipe(
            bloodhound.object_edges(obj),
            tuple,
        )

        assert len(edge_dicts) == bh_object_edge_counts[otype]


def test_object_edges_isa_first(bh_objects, bh_object_edge_counts):
    for otype, obj in bh_objects.items():
        edge_dicts = pipe(
            bloodhound.object_edges(obj),
            tuple,
        )

        isa_edge = edge_dicts[0]
        assert isa_edge['rel'] == 'IsA'



def test_object_edges_check_correct_types(bh_objects, bh_object_edge_counts):
    for otype, obj in bh_objects.items():
        edge_dicts = pipe(
            bloodhound.object_edges(obj),
            tuple,
        )

        isa_edge = edge_dicts[0]
        match isa_edge:
            case {'a': o_sid, 'b': 'AIACA'}:
                assert otype == 'aiacas'
                assert o_sid == 'C4A66CF4-0FEA-44FA-B65E-6553F7C3BDD4' 
            case {'a': o_sid, 'b': 'CertTemplate'}:
                assert otype == 'certtemplates'
                assert o_sid == 'C972D130-3753-414A-B193-166DF2386800' 
            case {'a': o_sid, 'b': 'Computer'}:
                assert otype == 'computers'
                assert o_sid == 'S-1-5-21-2697957641-2271029196-387917394-2164' 
            case {'a': o_sid, 'b': 'Container'}:
                assert otype == 'containers'
                assert o_sid == '04F9AEFD-BFC5-4B9F-887C-FFC7F72B74F0' 
            case {'a': o_sid, 'b': 'Domain'}:
                assert otype == 'domains'
                assert o_sid == 'S-1-5-21-2697957641-2271029196-387917394' 
            case {'a': o_sid, 'b': 'EnterpriseCA'}:
                assert otype == 'enterprisecas'
                assert o_sid == 'CEC2A22A-AF46-4DC5-A942-26514BD8AE94' 
            case {'a': o_sid, 'b': 'GPO'}:
                assert otype == 'gpos'
                assert o_sid == 'A12512B2-7103-4BEF-B528-50681B3796AB' 
            case {'a': o_sid, 'b': 'Group'}:
                assert otype == 'groups'
                assert o_sid == 'S-1-5-21-2697957641-2271029196-387917394-2152' 
            case {'a': o_sid, 'b': 'NTAuthStore'}:
                assert otype == 'ntauthstores'
                assert o_sid == '2F9F3630-F46A-49BF-B186-6629994EBCF9' 
            case {'a': o_sid, 'b': 'OU'}:
                assert otype == 'ous'
                assert o_sid == '2A2B238D-7CD4-45FD-964A-A402A9752B2E' 
            case {'a': o_sid, 'b': 'RootCA'}:
                assert otype == 'rootcas'
                assert o_sid == 'FA4FB111-ADDB-4320-951C-39F909ED2B1D' 
            case {'a': o_sid, 'b': 'User'}:
                assert otype == 'users'
                assert o_sid == 'S-1-5-21-2697957641-2271029196-387917394-2216' 


