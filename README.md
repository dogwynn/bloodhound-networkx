# bloodhound-networkx

Tools to ingest JSON BloodHound graph data into a NetworkX graph. Currently, it only works with "community edition" formatted JSON.

## Install

Using `pip`:

```
pip install bloodhound-networkx
```

## Usage (CLI)

There is a CLI interface, `bnx-cli`: 

```
$ bnx-cli --help
Usage: bnx-cli [OPTIONS] COMMAND [ARGS]...

Options:
  --loglevel [debug|info|warning|error]
  --help                          Show this message and exit.

Commands:
  list-groups  List the AD Group objects.
  list-users   List the AD User objects.
  process      Process either a selection of JSON files or a directory...
```

### bnx-cli process

This "processes" the Bloodhound JSON data into a gzipped-pickled version of the NetworkX graph.

```
$ bnx-cli process --help
Usage: bnx-cli process [OPTIONS] JSON_PATHS_OR_DIR...

  Process either a selection of JSON files or a directory containing JSON
  files.  Will save the graph data as a pickled then GZIPed NetworkX
  MultiDiGraph.  If a stem (-o/--output-stem) is provided, then that will be
  the name of the  saved file (plus '.pkl.gz'), otherwise the name of the
  shared parent directory  of all of the JSON files will be used as the
  filename. If they don't share a  common parent, then -o/--output-stem is
  required.

Options:
  -o, --output-stem TEXT  Filename stem for output graph data. Will use the
                          parent directory name of the  JSON files if they
                          share a common parent. If they do not share a common
                          parent, then this is required.
  --output-dir TEXT       Directory to output the graph data
  --force
  --help                  Show this message and exit.
```

For example:

```
$ cd bloodhound-networkx
$ ls tests/data/ad_sampledata/20240305110427
20240305110427_computers.json   20240305110427_domains.json  
20240305110427_groups.json  20240305110427_users.json
20240305110427_containers.json  20240305110427_gpos.json     
20240305110427_ous.json
$ bnx-cli process ./tests/data/ad_sampledata/20240305110427
2026-06-28 14:19:35 INFO   [bloodhound_networkx.cli.process: 104]  Saving NetworkX graph data to: 20240305110427.pkl.gz
```

### bnx-cli list-users

This will list all AD User objects in the Bloodhound data. Can pass it either JSON or an already "processed" graph.

```
$ bnx-cli list-users --help
Usage: bnx-cli list-users [OPTIONS] JSON_OR_GRAPH...

  List the AD User objects. Must provide either a path to a persisted graph
  (from an earlier process call) or valid JSON paths/dir. By default, will
  print to stdout unless -o/--output-path is given.

Options:
  -o, --output-path TEXT  File path to output user data
  --disabled
  -c, --column TEXT       Columns desired in the output. If not provided, then
                          samaccountname will be used. Use -c/--column
                          multiple times for multiple columns.
  --column-counts         Print to stdout all the columns available for User
                          objects, with counts of non-zero values
  --columns-all-true      Only print a row if all of its values are "true"
                          (not False, empty, or null/None)
  --help                  Show this message and exit.
```

For example: 

```
$ bnx-cli list-users 20240305110427.pkl.gz 
BH@GHOST.CORP
ADMINISTRATOR@GHOST.CORP

$ bnx-cli list-users 20240305110427.pkl.gz --disabled
BH@GHOST.CORP
TOM@GHOST.CORP
WALTER@GHOST.CORP
ADMINISTRATOR@GHOST.CORP
GUEST@GHOST.CORP
KRBTGT@GHOST.CORP
NETWORK SERVICE@GHOST.CORP

$ # There is a --column-counts option you can use to find which columns
# #   each User object has.
$ bnx-cli list-users 20240305110427.pkl.gz --column-counts
    2: admincount
    2: description
    2: displayname
    2: distinguishedname
    2: domain
    2: domainsid
    2: dontreqpreauth
    2: email
    2: enabled
    2: hasspn
    2: homedirectory
    2: isaclprotected
    2: lastlogon
    2: lastlogontimestamp
    2: logonscript
    2: name
    2: passwordnotreqd
    2: pwdlastset
    2: pwdneverexpires
    2: samaccountname
    2: sensitive
    2: serviceprincipalnames
    2: sfupassword
    2: sid
    2: sidhistory
    2: title
    2: trustedtoauth
    2: type                     # This is added: 'User', 'Group', etc.
    2: unconstraineddelegation
    2: unicodepassword
    2: unixpassword
    2: userpassword
    2: whencreated


$ bnx-cli list-users 20240305110427.pkl.gz --disabled  -c name  -c enabled -c admincount | column -t -s $'\t'
BH@GHOST.CORP               True   True
TOM@GHOST.CORP              False  True
WALTER@GHOST.CORP           False  True
ADMINISTRATOR@GHOST.CORP    True   True
GUEST@GHOST.CORP            False  False
KRBTGT@GHOST.CORP           False  True
NETWORK SERVICE@GHOST.CORP     
```

### bnx-cli list-users

This will list all AD Group objects in the Bloodhound data. Can pass it either JSON or an already "processed" graph.

```
$ bnx-cli list-groups --help 
Usage: bnx-cli list-groups [OPTIONS] JSON_OR_GRAPH...

  List the AD Group objects. Must provide either a path to a persisted graph
  (from an earlier process call) or valid JSON paths/dir. By default, will
  print to stdout unless -o/--output-path is given.

Options:
  -o, --output-path TEXT  File path to output group data
  -c, --column TEXT       Columns desired in the output. If not provided, then
                          name will be used. Use -c/--column multiple times
                          for multiple columns.
  --column-counts         Print to stdout all the columns available for Group
                          objects, with counts of non-zero values
  --columns-all-true      Only print a row if all of its values are "true"
                          (not False, empty, or null/None)
  --help                  Show this message and exit.

```
