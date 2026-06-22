import typing as T
from pathlib import Path
import pprint

import networkx as nx

from .common import new_log
from .toolz import (
    pipe, json_slurp, merge, mapcat, map, endswith, first, filter, vfilter,
    curry, concat, concatv,
)

log = new_log(__name__)

def graph_path(G: nx.MultiDiGraph):
    return G.nodes['__metadata__']['path']

@curry
def ids_by_type(node_type: str, G: nx.MultiGraph):
    return pipe(
        G.in_edges(node_type),
        map(first),
        tuple,
    )
user_ids = ids_by_type('User')
computer_ids = ids_by_type('Computer')
group_ids = ids_by_type('Group')
ou_ids = ids_by_type('OU')
container_ids = ids_by_type('Container')
gpo_ids = ids_by_type('GPO')
domain_ids = ids_by_type('Domain')

@curry
def nodes_by_type(node_type: str, G: nx.MultiDiGraph):
    return pipe(
        ids_by_type(node_type, G),
        map(G.nodes.get),
        filter(None),
        tuple,
    )
users = nodes_by_type('User')
computers = nodes_by_type('Computer')
groups = nodes_by_type('Group')
ous = nodes_by_type('OU')
containers = nodes_by_type('Container')
gpos = nodes_by_type('GPO')
domains = nodes_by_type('Domain')

def domain_ids(G: nx.MultiGraph):
    return pipe(
        G.in_edges('Domain'),
        map(first),
        tuple,
    )
def domains(G: nx.MultiGraph):
    return pipe(
        domain_ids(G),
        map(G.nodes.get),
        tuple,
    )

_sids = {}

@curry
def by_end_digit(end: str, G: nx.MultiDiGraph):
    sid_end = ('-' if not end.startswith('-') else '') + end
    k = (graph_path(G), sid_end)
    if k in _sids:
        return _sids[k]
    
    sids = pipe(
        G, filter(endswith(sid_end)), tuple,
    )
    if sids:
        _sids[k] = sids[0]
        return sids[0]
    log.error(f'No node in this graph with SID: {sid_end}')

domain_admin_id = by_end_digit('512')
def domain_admins(G: nx.MultiDiGraph):
    return G.nodes[domain_admin_id(G)]

domain_users_id = by_end_digit('513')
def domain_users(G: nx.MultiDiGraph):
    return G.nodes[domain_users_id(G)]

users_id = by_end_digit('545')
def users(G: nx.MultiDiGraph):
    return G.nodes[users_id(G)]

authorized_users_id = by_end_digit('11')
def authorized_users(G: nx.MultiDiGraph):
    return G.nodes[authorized_users_id(G)]



abuse_rights = set([
    'Owns', 'GenericAll', 'GenericWrite', 'WriteOwner', 'WriteDacl', 'MemberOf',
    'ForceChangePassword', 'AllExtendedRights', 'AddMember', 'AllowedToDelegate',
    'CoerceToTGT', 'AllowedToAct', 'AdminTo', 'CanPSRemote', 'CanRDP',
    'ExecuteDCOM', 'HasSIDHistory', 'AddSelf', 'DCSync', 'ReadLAPSPassword',
    'ReadGMSAPassword', 'DumpSMSAPassword', 'SQLAdmin', 'AddAllowedToAct',
    'WriteSPN', 'AddKeyCredentialLink', 'SyncLAPSPassword',
    'WriteAccountRestrictions', 'WriteGPLink', 'GoldenCert', 'ADCSESC1',
    'ADCSESC3', 'ADCSESC4', 'ADCSESC6a', 'ADCSESC6b', 'ADCSESC9a', 'ADCSESC9b',
    'ADCSESC10a', 'ADCSESC10b', 'ADCSESC13', 'SyncedToEntraUser',
    'CoerceAndRelayNTLMToSMB', 'CoerceAndRelayNTLMToADCS',
    'WriteOwnerLimitedRights', 'OwnsLimitedRights', 'CoerceAndRelayNTLMToLDAP',
    'CoerceAndRelayNTLMToLDAPS', 'HasTrustKeys', 'DCFor', 'SameForestTrust',
    'SpoofSIDHistory', 'AbuseTGTDelegation'
])

@curry
def rights_edge_types(rights: T.Sequence[T.Tuple[str, str, str]]):
    return set(concatv(rights, ['IsA']))

abuse_rights_edge_types = rights_edge_types(abuse_rights)

def domain_users_to_any_user_edges(G: nx.MultiDiGraph):
    sG = nx.edge_subgraph(G, pipe(
        G.edges,
        vfilter(lambda a, b, type: type in abuse_rights_edge_types),
    ))
    return pipe(
        nx.all_simple_edge_paths(sG, domain_users_id(G), 'User'),
        map(lambda P: tuple(P)[:-1]),
        tuple,
    )

@curry
def node_to_node_with_edge_1(n_type_a: str, n_type_b: str, e_type: str, 
                             G: nx.MultiDiGraph):
    a_ids = set(ids_by_type(n_type_a, G))
    b_ids = set(ids_by_type(n_type_b, G))

    edges = pipe(
        G.edges,
        vfilter(lambda a, b, et: (
            a in a_ids and b in b_ids and et == e_type
        )),
        tuple,
    )

    return edges