import typing as T
from pathlib import Path

import click
import networkx as nx

from ..common import new_log
from ..toolz import (
    pipe, map, vmap, filter, vfilter, compose_left, get, get_in, noop, mapcat, 
    keys, most_common, sort_by,
)
from .common import bnx_cli
from .. import bloodhound
from .. import networkx
from .. import analysis

log = new_log(__name__)

def process_json_paths(json_paths_or_dir):
    paths = []
    match json_paths_or_dir:
        case (one_path,):
            path = Path(one_path)
            if path.exists() and path.is_dir():
                paths = tuple(path.glob('*.json'))
            else:
                paths = (path,)
        case many_paths:
            paths = [Path(p) for p in many_paths]
    return paths

def json_paths_to_graph(json_paths: T.Iterable[Path]) -> nx.MultiDiGraph:
    return pipe(
        json_paths,
        bloodhound.parse_files,
        networkx.to_digraph,
    )

def process_json_or_graph(json_or_graph) -> nx.MultiDiGraph:
    if len(json_or_graph) == 1 and json_or_graph[0].endswith('pkl.gz'):
        return networkx.unpickle_graph(json_or_graph[0])
    else:
        return pipe(
            json_or_graph,
            process_json_paths,
            json_paths_to_graph,
        )

@bnx_cli.command(help='''
Process either a selection of JSON files or a directory containing JSON files. 
Will save the graph data as a pickled then GZIPed NetworkX MultiDiGraph. 
If a stem (-o/--output-stem) is provided, then that will be the name of the 
saved file (plus '.pkl.gz'), otherwise the name of the shared parent directory 
of all of the JSON files will be used as the filename. If they don't share a 
common parent, then -o/--output-stem is required.
''')
@click.argument('json-paths-or-dir', nargs=-1, required=True, 
                type=click.Path(exists=True))
@click.option('-o', '--output-stem', help='''
Filename stem for output graph data. Will use the parent directory name of the 
JSON files if they share a common parent. If they do not share a common parent,
then this is required.
''')
@click.option('--output-dir', default='.', help='Directory to output the graph data')
@click.option('--force', is_flag=True)
def process(json_paths_or_dir: T.Sequence[str], output_stem: str, output_dir: str,
            force: bool):
    paths = process_json_paths(json_paths_or_dir)

    if output_stem is None:
        parents = pipe(
            paths,
            map(lambda p: p.parent),
            set,
            tuple,
        )
        if len(parents) == 1:
            output_stem = parents[0].name
        else:
            raise click.UsageError(
                'Must provide -o/--output-stem if JSON files do not share'
                ' same parent.'
            )


    output_dir_path = Path(output_dir)
    if not output_dir_path.exists():
        log.info(
            f'Output dir {output_dir_path} does not exist... creating.'
        )
        output_dir_path.mkdir(parents=True)

    output_path = networkx.pickle_path(output_dir_path, output_stem)

    if output_path.exists() and not force:
        if not click.confirm(
            f'Do you wish to overwrite {output_path} ?', 
            default=False, show_default=True
        ):
            click.echo('Aborting...')
            return

    G = json_paths_to_graph(paths)
    log.info(
        f'Saving NetworkX graph data to: {output_path}'
    )
    networkx.pickle_graph(output_dir_path, output_stem, G)

@bnx_cli.command(help='''
List the AD User objects. Must provide either a path to a persisted graph 
(from an earlier process call) or valid JSON paths/dir. By default, will 
print to stdout unless -o/--output-path is given.
''')
@click.argument('json-or-graph', required=True, nargs=-1, type=click.Path(exists=True))
@click.option('-o', '--output-path', help='File path to output user data',)
@click.option('--disabled', is_flag=True)
@click.option('-c', '--column', multiple=True, help='''
Columns desired in the output. If not provided, then "name" will be used.
Use -c/--column multiple times for multiple columns.
''')
@click.option('--column-counts', is_flag=True, help='''
Print to stdout all the columns available for User objects, with counts of non-zero values
''')
@click.option('--columns-all-true', is_flag=True, help='''
Only print a row if all of its values are "true" (not False, empty, or null/None)
''')
def list_users(json_or_graph: T.Sequence[str], output_path: str, disabled: bool,
               column: T.Sequence[str], column_counts: bool, 
               columns_all_true: bool):
    G: nx.MultiDiGraph = process_json_or_graph(json_or_graph)

    enabled_filter = filter(get('enabled', default=False)) if not disabled else noop
    not_empty_filter = filter(lambda t: all(t)) if columns_all_true else noop

    if column_counts:
        pipe(
            analysis.all_users(G),
            enabled_filter,
            mapcat(keys),
            most_common,
            map(reversed),
            map(tuple),
            sort_by(lambda t: (t[0], t[1])),
            vmap(lambda c, k: f'{c:>5}: {k}'),
            '\n'.join,
            print,
        )
        return

    outputter = Path(output_path).write_text if output_path else print

    formatter = compose_left(map(map(str)), map('\t'.join),'\n'.join)

    columns = list(column) if column else ['name']

    pipe(
        analysis.all_users(G),
        enabled_filter,
        map(get(columns, default='')),
        not_empty_filter,
        filter(None),
        formatter,
        outputter,
    )


@bnx_cli.command(help='''
List the AD Group objects. Must provide either a path to a persisted graph 
(from an earlier process call) or valid JSON paths/dir. By default, will 
print to stdout unless -o/--output-path is given.
''')
@click.argument('json-or-graph', required=True, nargs=-1, type=click.Path(exists=True))
@click.option('-o', '--output-path', help='File path to output group data',)
@click.option('-c', '--column', multiple=True, help='''
Columns desired in the output. If not provided, then name will be used.
Use -c/--column multiple times for multiple columns.
''')
@click.option('--column-counts', is_flag=True, help='''
Print to stdout all the columns available for Group objects, with counts of non-zero values
''')
@click.option('--columns-all-true', is_flag=True, help='''
Only print a row if all of its values are "true" (not False, empty, or null/None)
''')
def list_groups(json_or_graph: T.Sequence[str], output_path: str,
                column: T.Sequence[str], column_counts: bool, 
                columns_all_true: bool):
    G: nx.MultiDiGraph = process_json_or_graph(json_or_graph)

    not_empty_filter = filter(lambda t: all(t)) if columns_all_true else noop

    if column_counts:
        pipe(
            analysis.all_groups(G),
            mapcat(keys),
            most_common,
            map(reversed),
            map(tuple),
            sort_by(lambda t: (t[0], t[1])),
            vmap(lambda c, k: f'{c:>5}: {k}'),
            '\n'.join,
            print,
        )
        return

    outputter = Path(output_path).write_text if output_path else print

    formatter = compose_left(map(map(str)), map('\t'.join),'\n'.join)

    columns = list(column) if column else ['name']

    pipe(
        analysis.all_groups(G),
        map(get(columns, default='')),
        not_empty_filter,
        filter(None),
        formatter,
        outputter,
    )


