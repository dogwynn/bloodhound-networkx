import typing as T
from pathlib import Path
import pprint

from .common import new_log
from .toolz import (
    pipe, json_slurp, merge, mapcat, map,
)

log = new_log(__name__)

SUPPORTED_VERSIONS = [
    6,
]

class WrongBloodhoundVersion(Exception):
    pass

def check_version(data: dict):
    match data:
        case {'meta': {'version': version}}:
            if version in SUPPORTED_VERSIONS:
                return True
            else:
                log.error(
                    f'Version {version} is not in supported versions.'
                )
        case unparseable:
            log.error(
                f'Could not get version from "meta" key: \n'
                '\n'
                f'{pprint.pformat(unparseable.get("meta", {}))}'
            )
    return False


def parse_bloodhound_path(path: str | Path) -> T.Iterable[dict]:
    all_data = pipe(
        Path(path).expanduser(),
        json_slurp,
    )

    if not check_version(all_data):
        raise WrongBloodhoundVersion(
            'This JSON is an unsupported Bloodhound data version:\n'
            '\n'
            f'{pprint.pformat(all_data.get("meta", {}))}'
        )

    bh_type: str = all_data['meta']['type']

    return pipe(
        all_data['data'],
        map(lambda d: merge(d, {'type': bh_type})),
    )

def object_type(obj: dict):
    return {
        'aiacas': 'AIACA',
        'certtemplates': 'CertTemplate',
        'computers': 'Computer',
        'containers': 'Container',
        'domains': 'Domain',
        'enterprisecas': 'EnterpriseCA',
        'gpos': 'GPO',
        'groups': 'Group',
        'ntauthstores': 'NTAuthStore',
        'ous': 'OU',
        'rootcas': 'RootCA',
        'users': 'User',
    }.get(obj['type'], 'Base')

def object_properties(obj: dict):
    return merge(obj['Properties'], {
        'type': object_type(obj),
        'sid': obj['ObjectIdentifier'],
    })
        
localgroup_sid_to_edge = {
    '544': 'AdminTo',
    '555': 'CanRDP',
    '562': 'ExecuteDCOM',
    '580': 'CanPSRemote',
}

class EdgeDict(T.TypedDict):
    a: str
    b: str
    rel: str
    meta: dict

def object_edges(obj: dict) -> T.Generator[EdgeDict]:
    this_sid = obj['ObjectIdentifier']

    yield {
        'a': this_sid,
        'b': object_type(obj),
        'rel': 'IsA',
    }

    ace_principal_rights = {}
    for ace in obj['Aces']:
        ace_principal_rights.setdefault(ace['PrincipalSID'], set()).add(ace['RightName'])

        yield {
            'a': ace['PrincipalSID'],
            'b': this_sid,
            'rel': ace['RightName'],
            'meta': {
                'inherit': ace['IsInherited'],
            },
        }

    # computers
    for group in obj.get('LocalGroups', []):
        lg_sid = group['ObjectIdentifier'].split('-')[-1]
        for entity in group.get('Results', []):
            ent_sid = entity['ObjectIdentifier']
            if lg_sid in localgroup_sid_to_edge:
                yield {
                    'a': ent_sid,
                    'b': this_sid,
                    'rel': localgroup_sid_to_edge[lg_sid],
                }

    if 'ContainedBy' in obj and obj['ContainedBy']:
        c_sid = obj['ContainedBy']['ObjectIdentifier']
        yield {
            'a': this_sid,
            'b': c_sid,
            'rel': 'MemberOf',
        }
    
    # groups
    for member in obj.get('Members', []):
        yield {
            'a': member['ObjectIdentifier'],
            'b': this_sid,
            'rel': 'MemberOf',
        }

    # ous and domains
    for link in obj.get('Links', []):
        yield {
            'a': this_sid,
            'b': link['GUID'],
            'rel': 'GPOLink',
            'meta': {
                'enforced': link['IsEnforced'],
            },
        }

    # domains
    for principal_sid in ace_principal_rights:
        if {'GetChanges', 'GetChangesAll'}.issubset(ace_principal_rights[principal_sid]):
            yield {
                'a': principal_sid,
                'b': this_sid,
                'rel': 'DCSync',
            }


    # ous and domains and containers
    for child in obj.get('ChildObjects', []):
        yield {
            'a': this_sid,
            'b': child['ObjectIdentifier'],
            'rel': 'Contains',
        }


def parse_files(json_paths: T.Sequence[str | Path]) -> T.Iterable[dict]:
    return pipe(
        json_paths,
        mapcat(parse_bloodhound_path),
    )

def parse_directory(path: str | Path) -> T.Iterable[dict]:
    path = Path(path).expanduser()
    if not path.exists():
        log.error(
            f"Path does not exist: {path}"
        )
        return
    json_paths = list(path.glob('*.json'))
    if not json_paths:
        log.error(
            f'No JSON files in directory at {path}'
        )

    return parse_files(json_paths)


