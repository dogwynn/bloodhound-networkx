import io
import collections
from pathlib import Path
from argparse import ArgumentError
import random
import functools
import builtins
from typing import (
    Union, Optional, Callable, Any, Hashable,
)
import json
import gzip
import bz2

from toolz.curried import (
    accumulate, apply, assoc, assoc_in, comp,
    complement, compose, compose_left, concat, concatv,
    cons, count, countby, curry, diff,
    dissoc, do, drop, excepts, filter,
    first, flip, frequencies, get, get_in,
    groupby, identity, interleave, interpose, isdistinct,
    isiterable, itemfilter, itemmap, iterate, join,
    juxt, keyfilter, keymap, last, map,
    mapcat, memoize, merge, merge_sorted, merge_with,
    nth, operator, partial, partition, partition_all,
    partitionby, peek, peekn, pipe, pluck,
    reduce, reduceby, remove, second,
    sliding_window, sorted, tail, take, take_nth,
    thread_first, thread_last, topk, unique, update_in,
    valfilter, valmap,
)

def noop(value):
    '''Yes, we have no banana pudding.

    Examples:

    >>> noop(1)
    1
    >>> noop("Banana Pudding")
    'Banana Pudding'
    '''
    return value


# ---------------------------
# String in-line functions
# ---------------------------

streamable = str | bytes | io.IOBase

def to_io(value: streamable):
    match value:
        case io_obj if isinstance(io_obj, io.IOBase):
            return io_obj
        case value_b if isinstance(value_b, bytes):
            return io.BytesIO(value_b)
        case value_s if isinstance(value_s, str):
            return io.StringIO(value_s)
        case _:
            raise IOError(
                f'Cannot deal with type {type(value)}'
            )

def strip(chars: Optional[str] = None, value: str = None):
    '''In-line string strip function

    Examples:

    >>> strip(None, '  a  ') == 'a'
    True
    >>> pipe('  a  ', strip()) == 'a'
    True
    >>> pipe('---a----', strip('-')) == 'a'
    True
    >>> pipe('---a----', strip(chars='-')) == 'a'
    True
    '''
    if value is not None:
        return value.strip(chars)

    def strip_inner(*args):
        nonlocal value, chars
        match args, chars:
            case (), None:
                raise ArgumentError(
                    'Calling strip with neither chars nor value'
                )
            case (value,), None:
                pass
            case (value,), chars:
                pass
            case too_many, chars:
                raise ArgumentError(
                    f'Too many arguments: {len(too_many)} with chars {chars}'
                )
        return value.strip(chars)
    return strip_inner

def split(sep: Optional[str] = None, value: Optional[str] = None,  maxsplit=-1):
    '''In-line string split function

    Examples:

    >>> split(None, 'a b') == ['a', 'b']
    True
    >>> pipe('a b', split()) == ['a', 'b']
    True
    >>> pipe('a,b', split(','))
    ['a', 'b']
    '''
    if value is not None:
        return value.split(sep, maxsplit)

    def splitter(*args):
        nonlocal sep, value, maxsplit
        match args, sep:
            case (), None:
                raise ArgumentError(
                    'Calling split with neither sep or value'
                )
            case (value,), None:
                pass
            case (value,), sep:
                pass
            case too_many, sep:
                raise ArgumentError(
                    f'Too many arguments: {len(too_many)} with sep {sep}'
                )

        return value.split(sep, maxsplit)
    return splitter

@curry
def splitlines(value: streamable, keepends=False):
    '''
    In-line string splitlines function. Stream-safe.
    '''
    for line in to_io(value):
        if keepends:
            yield line
        else:
            if line.endswith('\n'):
                yield line[:-1]
            else:
                yield line

def lower(value: str):
    'In-line string lower function'
    return value.lower()

def upper(value: str):
    'In-line string upper function'
    return value.upper()

@curry
def startswith(prefix: Union[str, bytes], string: Union[str, bytes]):
    return string.startswith(prefix)

@curry
def endswith(prefix: Union[str, bytes], string: Union[str, bytes]):
    return string.endswith(prefix)

def do_slice(start: int, stop: int = None, step: int = None):
    def slicer(value: str):
        return value[start:stop:step]
    return slicer

@curry
def replace(old: str, new: str, value: str, count: int = -1):
    'In-line string replace'
    return value.replace(old, new, count)

# ---------------------------
# Dictionary in-line functions

def items(d: dict):
    'Items accessor for dictionaries'
    return d.items()

def values(d: dict):
    'Values accessor for dictionaries'
    return d.values()

def keys(d: dict):
    'Keys accessor for dictionaries'
    return d.keys()

# ----------------------------------------------------------------------
#
# Supplemental versions of toolz functions, especially variadic versions.
#
# ----------------------------------------------------------------------

@curry
def vcall(func, value):
    '''Variadic call

    Example:

    >>> pipe([1, 2], vcall(lambda a, b: a + b))
    3
    '''
    return func(*value)

@curry
def vmap(func, seq):
    '''Variadic map

    Example:

    >>> pipe([(2, 1), (2, 2), (2, 3)], vmap(lambda a, b: a ** b), tuple)
    (2, 4, 8)
    '''
    return pipe(
        seq,
        map(vcall(func)),
    )

@curry
def map_t(func, values):
    return pipe(
        values,
        map(func),
        tuple,
    )

starmap = vmap

@curry
def mapget(key, seq, *, default=None):
    '''map(get) combo

    Example:

    >>> pipe([{'a': 1}, {'a': 2}], mget('a'), sum) == 3
    True
    '''
    return pipe(
        seq,
        map(get(key, default=default)),
    )
mget = mapget

@curry
def vfilter(func, seq):
    '''Variadic filter

    Example:

    >>> pipe([(1, 2), (4, 3), (5, 6)], vfilter(lambda a, b: a < b), tuple)
    ((1, 2), (5, 6))
    '''
    return pipe(
        seq,
        filter(vcall(func)),
    )

@curry
def vmapcat(func, seq):
    '''Variadic mapcat

    Example:

    >>> pipe([(1, 2), (4, 3), (5, 6)], vmapcat(lambda a, b: [a] * b), tuple)
    (1, 1, 4, 4, 4, 5, 5, 5, 5, 5, 5)
    '''
    return pipe(
        seq,
        mapcat(vcall(func)),
    )

concat_t = compose_left(concat, tuple)
concatv_t = compose_left(concatv, tuple)

@curry
def slurp(path: str | Path, encoding: str = None):
    '''Read contents of file as str

    Examples:

    >>> with tempfile.TemporaryDirectory() as temp:
    ...     root = Path(temp)
    ...     path = root / 'test.txt'
    ...     _ = path.write_text('file content')
    ...     content = pipe(path, slurp)
    >>> content
    'file content'

    '''
    path = Path(path).expanduser()
    encoding = encoding or 'utf-8'
    try:
        return path.read_text(encoding)
    except UnicodeDecodeError as unicode_err:
        try:
            encoding = 'cp1252'
            return path.read_text(encoding)
        except:
            return path.read_text('utf-8', errors='ignore')
    
@curry
def slurplines(path: Path, n: int = None, **open_kw):
    path = Path(path).expanduser()

    def merge_kws(**kw):
        return merge(open_kw, kw)
    
    try:
        with path.open(**open_kw) as rfp:
            for i, line in enumerate(rfp):
                if n is not None and i == n:
                    break
                yield line.rstrip('\n')
    except UnicodeDecodeError as unicode_err:
        try:
            encoding = 'cp1252'
            yield from slurplines(path, n=n, **merge_kws(encoding=encoding))
        except:
            yield from slurplines(path, n=n, **merge_kws(errors='ignore'))

def slurpb(path: str | Path):
    '''Read contents of file as bytes

    Examples:

    >>> with tempfile.TemporaryDirectory() as temp:
    ...     root = Path(temp)
    ...     path = root / 'test.txt'
    ...     _ = path.write_text('file content')
    ...     content = pipe(path, slurpb)
    >>> content
    b'file content'

    '''
    path = Path(path).expanduser()
    return path.read_bytes()

# ----------------------------------------------------------------------
#
# JSON handling functions
#
# ----------------------------------------------------------------------


@curry
@functools.wraps(json.dumps)
def json_dumps(obj, **kw):
    if 'default' not in kw:
        kw['default'] = str
    return json.dumps(obj, **kw)

@curry
@functools.wraps(json.loads)
def json_loads(*a, **kw):
    return json.loads(*a, **kw)

def json_slurp(path: Path):
    path = Path(path).expanduser()
    decomp = {
        '.gz': gzip.decompress,
        '.bz2': bz2.decompress,
        '.bz': bz2.decompress,
    }
    if path.suffix in decomp:
        data = pipe(
            path,
            slurpb,
            decomp[path.suffix],
            lambda b: b.decode(errors='ignore'),
        )
    else:
        data = slurp(path)
    return json_loads(data)

@curry
def cdissoc(key: Hashable, d):
    ''' Curried dissoc

    Args:
      key (Hashable): key to be removed
    
      d (dict): dictionary to transform (with no side effects)

    Returns: (dict) new state of dictionary

    Examples:

    >>> pipe({'b': 2}, drop_key('b'))
    {}
    >>> pipe({'a': 2}, drop_key('b'))
    {'a': 2}
    
    '''
    return dissoc(d, key)
drop_key = cdissoc
remove_key = cdissoc

@curry
def cassoc(key: Hashable, value: Any, d: dict, factory=dict):
    '''Curried assoc

    Args:
      key (Hashable): key to be updated
    
      value (Any): value for the key

      d (dict): dictionary to transform (with no side effects)

    Returns: (dict) new state of dictionary

    Examples:

    >>> new = pipe({'b': 2}, cassoc('a', 5))
    >>> new == {'a': 5, 'b': 2}
    True

    '''
    return assoc(d, key, value, factory)
set_key = cassoc

