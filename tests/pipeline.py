import sys
from pyppl import PyPPL
from procs import pProcess1, pProcessInstallFail

pProcess1.input = 'a'
pProcess1.input = [1]
pProcess1.output = 'a:1'

pProcessInstallFail.input = 'a'
pProcessInstallFail.depends = pProcess1
pProcessInstallFail.output = 'a:1'

PyPPL().start(pProcess1).run()

sys.exit(1)