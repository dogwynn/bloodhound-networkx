import typing as T
from pathlib import Path
import pickle
import gzip

import networkx as nx

from .common import new_log
from .toolz import (
    pipe, mapcat, groupby, valmap, first, merge, map, endswith, filter, md5,
    json_dumps, concatv, do,
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

def to_digraph(bh_elements: T.Iterable[dict]):
    bh_elements = tuple(bh_elements)

    graph: nx.MultiDiGraph = pipe(
        bh_elements,
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
        bh_elements,
        map(bloodhound.object_properties),
        groupby('sid'),
        valmap(first),
    )
    nx.set_node_attributes(graph, node_attrs)

    g_hash = pipe(
        concatv(sorted(graph.nodes), sorted(graph.edges)),
        tuple,
        json_dumps,
        md5,
    )
    graph.add_node('__metadata__', **{
        'hash': g_hash,
    })

    return graph

def pickle_path(output_directory: Path, output_stem: str):
    return Path(output_directory) / f'{output_stem}.pkl.gz'

def pickle_graph(output_directory: Path, output_stem: str, G: nx.MultiDiGraph):
    output_path = pickle_path(output_directory, output_stem)
    with gzip.open(output_path, 'wb') as gz_wfp:
        pickle.dump(G, gz_wfp)

def unpickle_graph(path: Path) -> nx.MultiDiGraph:
    with gzip.open(path) as gz_rfp:
        return pickle.load(gz_rfp)
    
