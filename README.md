# pyppl_require

Requirement manager for processes of [PyPPL](https://github.com/pwwang/PyPPL).

## Installation
```shell
pip install pyppl_require
```

## Using API
```python
from pyppl import registerPlugins, Proc
# have to register before process definition
registerPlugins('pyppl_require')

proc = Proc(desc = 'A short description', long = '''
@requires:
  q:
    desc: A command line tool that allows direct execution of SQL-like queries on CSVs/TSVs
    url: http://harelba.github.io/q/index.html
    version: 1.7.1
    validate: "{{args.harelba_q}} -v"
    install: |
      wget https://cdn.rawgit.com/harelba/q/1.7.1/bin/q -O /tmp/q;
      chmod +x /tmp/q;
      sed -i 's@#!/usr/bin/env python@#!/usr/bin/env python2@' /tmp/q;
      install /tmp/q "{{args.harelba_q | ?.__contains__: '/' | =:_ | !:'$bindir$/'}}"
''')
proc.args.hrelba_q = '/bin/q'

proc.require_validate()
```

```shell
[proc] Validating q ... Failed.
[proc] Validation command: bash -c 'q -v'
[proc]   bash: q: command not found
```

```python
# ...
proc.require_install(bindir = '/home/usr/bin/')
```

```shell
[proc] Validating q ... Failed.
[proc] Validation command: bash -c 'q -v'
[proc]   bash: q: command not found
[proc] Installing q ...
[proc]   --2019-12-11 18:11:20--  https://cdn.rawgit.com/harelba/q/1.7.1/bin/q
[proc]   Resolving cdn.rawgit.com... 151.139.237.11
[proc]   Connecting to cdn.rawgit.com|151.139.237.11|:443... connected.
[proc]   HTTP request sent, awaiting response... 301 Moved Permanently
[proc]   Location: https://raw.githubusercontent.com/harelba/q/1.7.1/bin/q [following]
[proc]   --2019-12-11 18:11:20--  https://raw.githubusercontent.com/harelba/q/1.7.1/bin/q
[proc]   Resolving raw.githubusercontent.com... 199.232.28.133
[proc]   Connecting to raw.githubusercontent.com|199.232.28.133|:443... connected.
[proc]   HTTP request sent, awaiting response... 200 OK
[proc]   Length: 80435 (79K) [text/plain]
[proc]   Saving to: `/tmp/q'
[proc]
[proc]        0K .......... .......... .......... .......... .......... 63%  565K 0s
[proc]       50K .......... .......... ........                        100%  642K=0.1s
[proc]
[proc]   2019-12-11 18:11:20 (591 KB/s) - `/tmp/q' saved [80435/80435]
[proc]
[proc] Succeeded!
[proc] Validating q ... Installed.
```

## Using command-line tool

`my-pipeline.py`

```python
from pyppl import Proc, PyPPL
# no need to register before process definition

proc = Proc(desc = 'A short description', long = '''
@requires:
  q:
    desc: A command line tool that allows direct execution of SQL-like queries on CSVs/TSVs
    url: http://harelba.github.io/q/index.html
    version: 1.7.1
    validate: "{{args.harelba_q}} -v"
    install: |
      wget https://cdn.rawgit.com/harelba/q/1.7.1/bin/q -O /tmp/q;
      chmod +x /tmp/q;
      sed -i 's@#!/usr/bin/env python@#!/usr/bin/env python2@' /tmp/q;
      install /tmp/q "{{args.harelba_q | ?.__contains__: '/' | =:_ | !:'$bindir$/'}}"
''')
proc.args.hrelba_q = '/bin/q'

# but have to specify in PyPPL
PyPPL({
    'default': {'_plugins': ['pyppl_require']}
}).start(proc).require().run()
```

```shell
> pyppl-require --help
Description:
  Requirement manager for processes of PyPPL

Usage:
  pyppl-require <command> [OPTIONS]

Available commands:
  validate            - Validate if the requirements have been installed.
  install             - Install the requirements.
  help [COMMAND]      - Print help message for the command and exit.

> pyppl-require my-pipeline.py validate
[tsv.pTsvSql] Validating q ... Failed.
[tsv.pTsvSql] Validation command: bash -c 'q -v'
[tsv.pTsvSql]   bash: q: command not found

```

