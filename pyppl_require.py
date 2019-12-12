"""Requirement manager for processes of PyPPL"""

import sys
from os import path
from functools import partial
import importlib.util
from pathlib import Path
import cmdy
from diot import Diot
from pyparam import params
from pyppl.plugin import hookimpl, pluginmgr
from pyppl.logger import Logger

__version__ = "0.0.1"
logger      = Logger(name = 'pyppl_require')
incli       = False
pipelines   = []
next2run    = None

def _logger(msg, level):
	getattr(logger, level)('[pyppl_require] ' + msg)

def _loadPipeline(script):
	script = str(script)
	if not script.endswith('.py'):
		script = script + '.py'
	if not path.isfile(script):
		raise OSError("Pipeline script does not exist: {}".format(script))
	_logger('Loading pipeline script: %s' % script, 'info')
	spec = importlib.util.spec_from_file_location("mypipeline", script)
	spec.loader.exec_module(importlib.util.module_from_spec(spec))
	ret = importlib.util.module_from_spec(spec)
	#spec.loader.exec_module(ret)
	return ret

def _cliAddParams():
	params._desc         = 'Process requirement manager'
	params.pipe.required = True
	params.pipe.desc     = 'The pipeline script.'
	params.p             = params.pipe
	params.validate      = False
	params.validate.desc = 'Validate the requirements'
	params.install.desc  = ['Install the requirements. ',
		'You can specify a directory (default: /usr/bin) to install the requirements.']
	params.install.callback = lambda opt, ps: "Either --install or --validate is required." \
		if not ps.install.value and not ps.validate.value else None

def _validate(proc):
	if not proc.require:
		_logger("Requirements for process %r is not documented." % proc.name(), 'warning')
		return None
	failed = []
	for tool, info in proc.require.items():
		_logger(f"Validating {tool} ... ", 'info')
		cmd = cmdy.bash(c = info['validate'], _raise = False)
		if cmd.rc != 0:
			failed.append((tool, info))
			_logger("Failed.", 'error')
			_logger("Validation command: " + cmd.cmd, 'info')
			for err in cmd.stderr.splitlines():
				_logger(f"  {err}", 'error')
		else:
			_logger("Installed.", 'info')
	return failed

def _install(proc, bindir):
	failed = _validate(proc)
	if not failed:
		_logger('All requirements met, nothing to install.', 'info')
	else:
		for tool, info in failed:
			_logger('Installing %s ...' % tool, 'info')
			cmd = cmdy.bash(c = info['install'].replace('$bindir$', bindir),
				_iter = 'err', _raise = True)
			for line in cmd.__iter__():
				_logger(f'  {line}'.rstrip(), 'error')
			if cmd.rc != 0:
				_logger("Failed to install, please intall it manually.", 'error')
				_logger("  " + cmd.cmd, 'error')
			else:
				_logger("Succeeded!", 'info')
		_logger("Validating if it is a valid installation ...", 'info')
		_validate(proc)

@hookimpl
def pypplInit(ppl):
	for pipe in pipelines:
		if pipe is ppl:
			break
	else:
		pipelines.append(ppl)

@hookimpl
def pypplPreRun(ppl):
	if incli:
		global next2run
		next2run = ppl.tree.getNextToRun
		ppl.tree.getNextToRun = lambda: []

@hookimpl
def procInit(proc):
	proc.config.require = Diot()
	proc.props.requireValidate = partial(_validate, proc = proc)
	proc.props.requireInstall = partial(_install, proc = proc)

@hookimpl
def procBuildProps(proc):
	for req, info in proc.require.items():
		if 'validate' in info:
			info['validate'] = proc.template(info['validate']).render(dict(proc = proc, args = proc.args))
		if 'install' in info:
			info['install'] = proc.template(info['install']).render(dict(proc = proc, args = proc.args))

def console():
	global incli
	incli = True
	_cliAddParams()
	opts = params._parse(dict_wrapper = Diot)
	_loadPipeline(opts.pipe)

	for pipe in pipelines:
		_logger('pyppl_require: working on pipeline with start processes: %r' % pipe.tree.starts, 'info')
		proc = next2run()
		while proc:
			proc._buildProps()
			#proc._buildProcVars()
			if opts.install:
				proc.requireInstall(bindir = '/usr/bin' if opts.install is True else opts.install)
			else:
				proc.requireValidate()
			proc = next2run()

if not pluginmgr.has_plugin('pyppl_require'):
	pluginmgr.register(__import__('pyppl_require'))