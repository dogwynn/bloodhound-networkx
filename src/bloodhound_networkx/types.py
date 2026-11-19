import typing as T

class Ace(T.TypedDict):
    RightName: str
    IsInherited: bool
    PrincipalSID: str
    PrincipleType: str
    SubjectSID: str


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
    serviceprincipalnames: T.Sequence[str]
    hasspn: bool
    displayname: str
    email: str
    title: str
    homedirectory: str
    description: str
    userpassword: str
    admincount: bool
    sidhistory: T.Sequence[str]
    whencreated: int
    unixpassword: str
    unicodepassword: str
    logonscript: str
    samaccountname: str
    sfupassword: str

class SessionData(T.TypedDict):
    ComputerSID: str
    UserSID: str
class Sessions(T.TypedDict):
    Collected: bool
    FailureReason: str
    Results: T.Sequence[SessionData]

class ComputerData(T.TypedDict):
    name: str
    domain: str
    distinguishedname: str
    domainsid: str
    samaccountname: str
    haslaps: bool
    isaclprotected: bool
    description: str
    whencreated: int
    enabled: bool
    unconstraineddelegation: bool
    trustedtoauth: bool
    isdc: bool
    lastlogon: int
    lastlogontimestamp: int
    pwdlastset: int
    serviceprincipalnames: T.Sequence[str]
    email: str
    operatingsystem: str
    sidhistory: T.Sequence[str]
    allowedtodelegate: T.Sequence[str]



class ContainerData(T.TypedDict):
    domain: str
    name: str
    distinguishedname: str
    domainsid: str
    isaclprotected: bool

class GroupData(T.TypedDict):
    domain: str
    name: str
    domainsid: str
    distinguishedname: str
    samaccountname: str
    isaclprotected: bool
    whencreated: int
    admincount: bool
    description: str
    reconcile: bool
    description: str

class CertTemplatesData(T.TypedDict):
    domain: str
    name: str
    distinguishedname: str
    domainsid: str
    isaclprotected: bool
    description: str
    whencreated: int
    validityperiod: str
    renewalperiod: str
    schemaversion: int
    displayname: str
    oid: str
    enrollmentflag: str
    requiresmanagerapproval: bool
    nosecurityextension: bool
    certificatenameflag: str
    enrolleesuppliessubject: bool
    subjectaltrequireupn: bool
    subjectaltrequiredns: bool
    subjectaltrequiredomaindns: bool
    subjectaltrequireemail: bool
    subjectaltrequirespn: bool
    subjectrequireemail: bool
    ekus: list
    certificateapplicationpolicy: list
    authorizedsignatures: int
    applicationpolicies: list
    issuancepolicies: list
    effectiveekus: list
    authenticationenabled: bool

class EnterpriseCASData(T.TypedDict):
    domain: str
    name: str
    distinguishedname: str
    domainsid: str
    isaclprotected: bool
    description: str
    whencreated: int
    flags: str
    caname: str
    dnshostname: str
    certthumbprint: str
    certname: str
    certchain: list
    hasbasicconstraints: bool
    basicconstraintpathlength: int
    casecuritycollected: bool
    enrollmentagentrestrictionscollected: bool
    isuserspecifiessanenabledcollected: bool

class GPOData(T.TypedDict):
    domain: str
    name: str
    distinguishedname: str
    domainsid: str
    isaclprotected: bool
    description: str
    whencreated: int
    gpcpath: str

class NTAuthStoreData(T.TypedDict):
    domain: str
    name: str
    distinguishedname: str
    domainsid: str
    isaclprotected: bool
    certthumbprints: list
    description: str
    whencreated: int

class OUData(T.TypedDict):
    domain: str
    name: str
    distinguishedname: str
    domainsid: str
    isaclprotected: bool
    whencreated: int
    blocksinheritance: bool
    description: str

class RootCASData(T.TypedDict):
    domain: str
    name: str
    distinguishedname: str
    domainsid: str
    isaclprotected: bool
    description: str
    whencreated: int
    certthumbprint: str
    certname: str
    certchain: list
    hasbasicconstraints: bool
    basicconstraintpathlength: int

class DomainData(T.TypedDict):
    domain: str
    name: str
    distinguishedname: str
    domainsid: str
    isaclprotected: bool
    description: str
    whencreated: int
    functionallevel: str
    collected: bool


class AIACASData(T.TypedDict):
    domain: str
    name: str
    distinguishedname: str
    domainsid: str
    isaclprotected: bool
    description: str
    whencreated: int
    crosscertificatepair: list
    hascrosscertificatepair: bool
    certthumbprint: str
    certname: str
    certchain: list
    hasbasicconstraints: bool
    basicconstraintpathlength: int

class ObjectData(T.TypedDict):
    ObjectIdentifier: str
    ObjectType: str

class UserRight(T.TypedDict):
    Privilege: str
    Results: T.Sequence[ObjectData]
    LocalNames: list
    Collected: bool
    FailureReason: str

class Computer(T.TypedDict):
    PrimaryGroupSID: str
    AllowedToDelegate: list
    AllowedToAct: list
    HasSIDHistory: list
    DumpSMSAPassword: list
    Sessions: Sessions
    PrivilegedSessions: Sessions
    RegistrySessions: Sessions
    LocalGroups: T.Sequence[ObjectData]
    UserRights: T.Sequence[UserRight]
    DCRegistryData: dict
    IsDC: bool
    DomainSID: str
    Aces: T.Sequence[Ace]
    ObjectIdentifier: str
    IsDeleted: bool
    IsACLProtected: bool
    ContainedBy: dict | None
    Status: dict
    Properties: ComputerData


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

class Group(T.TypedDict):
    Members: list
    Aces: T.Sequence[Ace]
    ObjectIdentifier: str
    IsDeleted: bool
    IsACLProtected: bool
    type: str
    ContainedBy: dict
    Properties: GroupData

class Domain(T.TypedDict):
    GPOChanges: dict
    ChildObjects: list
    Trusts: list
    Links: list
    Aces: T.Sequence[Ace]
    ObjectIdentifier: str
    IsDeleted: bool
    IsACLProtected: bool
    ContainedBy: dict
    Properties: DomainData

class AIACAS(T.TypedDict):
    Aces: T.Sequence[Ace]
    ObjectIdentifier: str
    IsDeleted: bool
    IsACLProtected: bool
    ContainedBy: dict
    Properties: AIACASData

class CertTemplate(T.TypedDict):
    Aces: T.Sequence[Ace]
    ObjectIdentifier: str
    IsDeleted: bool
    IsACLProtected: bool
    ContainedBy: dict
    Properties: CertTemplatesData

class Container(T.TypedDict):
    ChildObjects: list
    ObjectIdentifier: str
    IsDeleted: bool
    IsACLProtected: bool
    ContainedBy: dict
    Aces: T.Sequence[Ace]
    Properties: ContainerData

class EnterpriseCAS(T.TypedDict):
    HostingComputer: str
    CARegistryData: dict
    EnabledCertTemplates: list
    Aces: T.Sequence[Ace]
    Properties: EnterpriseCASData
    ObjectIdentifier: str
    IsDeleted: bool
    IsACLProtected: bool
    ContainedBy: dict

class GPO(T.TypedDict):
    Aces: T.Sequence[Ace]
    Properties: GPOData
    ObjectIdentifier: str
    IsDeleted: bool
    IsACLProtected: bool
    ContainedBy: dict

class NTAuthStore(T.TypedDict):
    DomainSID: str
    Aces: T.Sequence[Ace]
    Properties: NTAuthStoreData
    ObjectIdentifier: str
    IsDeleted: bool
    IsACLProtected: bool
    ContainedBy: dict

class OU(T.TypedDict):
    GPOChanges: dict
    Links: list
    ChildObjects: list
    Aces: T.Sequence[Ace]
    Properties: OUData
    ObjectIdentifier: str
    IsDeleted: bool
    IsACLProtected: bool
    ContainedBy: dict

class RootCAS(T.TypedDict):
    DomainSID: str
    Aces: T.Sequence[Ace]
    Properties: RootCASData
    ObjectIdentifier: str
    IsDeleted: bool
    IsACLProtected: bool
    ContainedBy: dict

