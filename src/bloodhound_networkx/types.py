import typing as T


class UserData(T.TypedDict):
    name: str
    domain: str
    domainsid: str
    distinguishedname: str
    unconstraineddelegation: bool
    trustedtoauth: bool
    passwordnotreqd: bool
    enabled: bool
    lastlogon: int
    lastlogontimestamp: int
    pwdlastset: int
    dontreqpreauth: bool
    pwdneverexpires: bool
    sensitive: bool
    serviceprincipalnames: str
    hasspn: bool
    displayname: str
    email: str
    title: str
    homedirectory: str
    description: str
    userpassword: str
    admincount: bool
    sidhistory: str
    whencreated: int
    unixpassword: str
    unicodepassword: str
    logonscript: str
    samaccountname: str
    sfupassword: str

class ComputerData(T.TypedDict):
    pass

class ContainerData(T.TypedDict):
    pass

class Computer(T.TypedDict):
    pass

class Ace(T.TypedDict):
    RightName: str
    IsInherited: bool
    PrincipalSID: str
    PrincipleType: str
    SubjectSID: str

class User(T.TypedDict):
    AllowedToDelegate: list
    ObjectIdentifier: str
    PrimaryGroupSID: str
    ContainedBy: dict | None
    SPNTargets: list
    HasSIDHistory: list
    IsDeleted: bool
    IsACLProtected: bool
    Aces: T.Sequence[Ace]
    Properties: UserData
