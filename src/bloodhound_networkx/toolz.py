import io
import collections
from datetime import datetime
from pathlib import Path
from argparse import ArgumentError
import random
import functools
import builtins
import typing as T
from typing import (
    Union, Optional, Callable, Any, Hashable, Iterable,
)
import json
import gzip
import bz2
import hashlib
from collections import Counter
import tempfile

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
    >>> split("|", 'a|b') == ['a', 'b']
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
def splitlines(value: streamable, keepends=False) -> T.Generator[str]:
    r'''
    In-line string splitlines function. Stream-safe.
    
    >>> list(splitlines('a\nb')) == ['a', 'b']
    True
    >>> pipe('a\nb', splitlines, list) == ['a', 'b']
    True

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
    '''Pipe-able string lower function
    
    Example:

    >>> pipe(['A', 'B'], map(lower), list) == ['a', 'b']
    True
    '''
    return value.lower()

def upper(value: str):
    '''Pipe-able string upper function
    
    Example:

    >>> pipe(['a', 'b'], map(upper), list) == ['A', 'B']
    True
    '''
    return value.upper()

@curry
def startswith(prefix: Union[str, bytes], string: Union[str, bytes]):
    '''Pipe-able startswith

    Examples:

    >>> startswith('qw', 'qwer')
    True
    >>> pipe(['abc', 'xyz'], filter(startswith('a')), tuple) == ('abc',)
    True
    '''
    return string.startswith(prefix)

@curry
def endswith(prefix: Union[str, bytes], string: Union[str, bytes]):
    '''Pipe-able endswith

    Examples:

    >>> endswith('er', 'qwer')
    True
    >>> pipe(['abc', 'xyz'], filter(endswith('z')), tuple) == ('xyz',)
    True
    '''
    return string.endswith(prefix)

def do_slice(start: int, stop: int = None, step: int = None):
    def slicer(value: str):
        return value[start:stop:step]
    return slicer

@curry
def replace(old: str, new: str, value: str, count: int = -1):
    '''Pipe-able string replace

    Examples:

    >>> replace('a', 'b', 'aaa') == 'bbb'
    True
    >>> pipe(['asdf', 'bsdf'], map(replace('sdf', 'poo')), tuple) == ('apoo', 'bpoo')
    True
    
    '''
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
def vcall(func: T.Callable, value: T.Sequence[T.Any]):
    '''Variadic call

    Example:

    >>> pipe([1, 2], vcall(lambda a, b: a + b))
    3
    
    '''
    return func(*value)

@curry
def vmap(func: T.Callable, seq: T.Iterable[T.Sequence[T.Any]]):
    '''Variadic map

    Example:

    >>> pipe([(2, 1), (2, 2), (2, 3)], vmap(lambda a, b: a ** b), tuple)
    (2, 4, 8)
    '''
    return pipe(
        seq,
        map(vcall(func)),
    )

starmap = vmap

@curry
def map_t(func: T.Callable, values):
    '''Map function, then convert to tuple
    '''

    return pipe(
        values,
        map(func),
        tuple,
    )


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
def vfilter(func: T.Callable, seq):
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
def vmapcat(func: T.Callable, seq):
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

def most_common(obj: Union[Counter, Iterable[Hashable]]):
    match obj:
        case counter if isinstance(counter, Counter):
            return counter.most_common()
        case iterable:
            return pipe(
                iterable,
                Counter,
                lambda c: c.most_common(),
            )

def is_str(v):
    '''Is this a string object
    '''
    return isinstance(v, str)
is_not_string = complement(is_str)

def is_int(value):
    if type(value) is float:
        return False
    try:
        int(value)
    except ValueError:
        return False
    except TypeError:
        return False
    return True

@curry
@functools.wraps(builtins.sorted)
def sorted(iterable, **kw):
    '''Curried sorted

    Examples:

    >>> pipe([5, 2, 6], sorted)
    [2, 5, 6]
    '''
    return builtins.sorted(iterable, **kw)

@curry
def sort_by(func, iterable, **kw):
    '''Sort iterable by key=func

    Examples:

    >>> pipe([{'a': 1}, {'a': 8}, {'a': 2}], sort_by(get('a')))
    [{'a': 1}, {'a': 2}, {'a': 8}]
    '''
    if is_str(func) or is_int(func):
        func = get(func)

    return builtins.sorted(iterable, key=func, **kw)

def hash_content(hasher: Callable):
    def do_hash(content: Union[str, bytes]):
        if is_str(content):
            content = content.encode()
        return pipe(
            content,
            hasher,
            lambda h: h.hexdigest(),
        )
    return do_hash
md5 = hash_content(hashlib.md5)
sha1 = hash_content(hashlib.sha1)
sha256 = hash_content(hashlib.sha256)
sha512 = hash_content(hashlib.sha512)

def is_dict(d):
    return isinstance(d, collections.abc.Mapping)
is_not_dict = complement(is_dict)

def is_indexable(s):
    return hasattr(s, '__getitem__')

def is_seq(s):
    return (
        isinstance(s, collections.abc.Iterable)
        and                     # noqa
        (not is_dict(s))
        and                     # noqa
        (not isinstance(s, (str, bytes)))
    )
is_not_seq = complement(is_seq)

def is_float(value):
    try:
        float(value)
    except ValueError:
        return False
    except TypeError:
        return False
    return True

def is_numeric(value):
    if is_float(value) or is_int(value):
        return True
    return False

def to_builtins(obj):
    '''Attempt to convert object with non-builtin objects to builtin types

    '''
    match obj:
        case dobj if is_dict(obj):
            return pipe(
                dobj.items(),
                vmap(lambda k, v: (
                    to_builtins(k),
                    to_builtins(v)
                )),
                dict,
            )
        case seq if is_seq(seq):
            return pipe(seq, map(to_builtins), list)

    t_map = [
        (is_str, str),
        ((lambda o: isinstance(o, datetime)), str),
        ((lambda o: isinstance(o, Path)), str),
        (is_int, int),
        (is_float, float),
    ]

    for test_f, transform_f in t_map:
        if test_f(obj):
            return transform_f(obj)
    return obj


@curry
def hash_object(obj: Any, hash_func=md5):
    return pipe(
        obj,
        to_builtins,
        json_dumps(sort_keys=True),
        hash_func,
    )