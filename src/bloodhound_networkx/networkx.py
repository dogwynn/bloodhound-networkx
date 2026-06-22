from pathlib import Path

import networkx as nx

from .common import new_log
from .toolz import (
    pipe, mapcat, groupby, valmap, first, merge, map, endswith, filter,
)
from . import bloodhound

log = new_log(__name__)

def edges_to_dod(edges):
    dod = {}
    for edge in edges:
        match edge:
            case {'a': a, 'b': b, 'rel': rel, **rest}:
                if a not in dod:
                    dod[a] = {}
                if b not in dod[a]:
                    dod[a][b] = {}
                dod[a][b][rel] = merge(rest.values())
            case otherwise:
                log.error(
                    f'huh? {otherwise}'
                )
    return dod

def to_digraph(path: str | Path):
    nodes = pipe(
        path,
        bloodhound.parse_directory,
        tuple,
    )

    graph: nx.MultiDiGraph = pipe(
        nodes,
        mapcat(bloodhound.object_edges),
        edges_to_dod,
        lambda dod: nx.from_dict_of_dicts(
            dod, nx.MultiDiGraph, multigraph_input=True
        ),
    )
    auth_users = pipe(
        graph, filter(endswith('-11')), first,
    )
    dom_users = pipe(
        graph, filter(endswith('-513')), first,
    )
    everyone = pipe(
        graph, filter(endswith('-0')), first,
    )
    if (dom_users, auth_users) not in graph.edges:
        graph.add_edge(
            dom_users, auth_users, 'MemberOf'
        )
    if (auth_users, everyone) not in graph.edges:
        graph.add_edge(
            auth_users, everyone, 'MemberOf'
        )

    node_attrs = pipe(
        nodes,
        map(bloodhound.object_properties),
        groupby('sid'),
        valmap(first),
    )
    nx.set_node_attributes(graph, node_attrs)

    graph.add_node('__metadata__', **{
        'path': Path(path).expanduser().resolve(),
    })

    return graph
