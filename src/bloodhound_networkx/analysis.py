import typing as T
from pathlib import Path
import pprint
import hashlib

import networkx as nx

from .common import new_log
from .toolz import (
    pipe, json_slurp, merge, mapcat, map, endswith, first, filter, vfilter,
    curry, concat, concatv, hash_object,
)

log = new_log(__name__)

def graph_hash(G: nx.MultiDiGraph):
    return G.nodes['__metadata__']['hash']

@curry
def ids_by_type(node_type: str, G: nx.MultiGraph):
    return pipe(
        G.in_edges(node_type),
        map(first),
        tuple,
    )
all_user_ids = ids_by_type('User')
all_computer_ids = ids_by_type('Computer')
all_group_ids = ids_by_type('Group')
all_ou_ids = ids_by_type('OU')
all_container_ids = ids_by_type('Container')
all_gpo_ids = ids_by_type('GPO')
all_domain_ids = ids_by_type('Domain')

@curry
def nodes_by_type(node_type: str, G: nx.MultiDiGraph):
    return pipe(
        ids_by_type(node_type, G),
        map(G.nodes.get),
        filter(None),
        tuple,
    )
all_users = nodes_by_type('User')
all_computers = nodes_by_type('Computer')
all_groups = nodes_by_type('Group')
all_ous = nodes_by_type('OU')
all_containers = nodes_by_type('Container')
all_gpos = nodes_by_type('GPO')
all_domains = nodes_by_type('Domain')

_sids = {}
@curry
def id_by_end_digit(end: str, G: nx.MultiDiGraph):
    sid_end = ('-' if not end.startswith('-') else '') + end
    k = (graph_hash(G), sid_end)
    if k in _sids:
        return _sids[k]
    
    sids = pipe(
        G, filter(endswith(sid_end)), tuple,
    )
    if sids:
        _sids[k] = sids[0]
        return sids[0]
    log.error(f'No node in this graph with SID: {sid_end}')

@curry
def node_by_end_digit(end: str, G: nx.MultiDiGraph):
    return G.nodes[id_by_end_digit(end, G)]

domain_admins_id = id_by_end_digit('512')
domain_admins_node = node_by_end_digit('512')

administrators_id = id_by_end_digit('544')
administrators_node = node_by_end_digit('544')

domain_users_id = id_by_end_digit('513')
domain_users_node = node_by_end_digit('513')

users_id = id_by_end_digit('545')
users_node = node_by_end_digit('545')

authorized_users_id = id_by_end_digit('11')
authorized_users_node = node_by_end_digit('11')



abuse_rights = {
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
}

@curry
def rights_edge_types(rights: T.Sequence[T.Tuple[str, str, str]]):
    return set(concatv(rights, ['IsA']))

abuse_rights_edge_types = rights_edge_types(abuse_rights)

def abuse_subgraph(G: nx.MultiDiGraph):
    return nx.edge_subgraph(G, pipe(
        G.edges,
        vfilter(lambda a, b, type: type in abuse_rights_edge_types),
    ))

def domain_users_to_any_user_paths(G: nx.MultiDiGraph):
    sG = abuse_subgraph(G)
    return pipe(
        nx.all_simple_edge_paths(sG, domain_users_id(G), 'User'),
        map(lambda P: tuple(P)[:-1]),
        tuple,
    )

Edge = T.Tuple[str, str, str]

@curry
def edge_to_str(G: nx.MultiDiGraph, edge: Edge) -> str:
    a, b, etype = edge
    return f'{G.nodes[a]["name"]} --[{etype}]-> {G.nodes[b]["name"]}'

@curry
def edges_to_str(G: nx.MultiDiGraph, edges: T.Iterable[Edge]):
    return pipe(
        edges,
        map(edge_to_str(G)),
        '\n'.join,
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