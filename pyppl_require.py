"""Requirement manager for processes of PyPPL"""
import sys
import importlib
from pathlib import Path
import toml
import cmdy
from diot import OrderedDiot
from pyppl.plugin import hookimpl
from pyppl.logger import Logger
from pyppl.pyppl import PIPELINES, PROCESSES

# pylint: disable=unused-argument

REQUIRE_FLAG = False
logger = Logger(plugin='require') # pylint: disable=invalid-name


def load_pipeline(pipeline):
    """Load pipelines from path
    If loaded, they should be in PIPELINES
    """
    global REQUIRE_FLAG # pylint: disable=global-statement
    pipeline = Path(pipeline)
    logger.info('Loading pipelines from %s', pipeline)
    if '/' not in str(pipeline):
        pipeline = Path(cmdy.which(pipeline).strip())
    if not pipeline.is_file():
        logger.error("Pipeline script does not exist: %s", pipeline)
        sys.exit(1)

    spec = importlib.util.spec_from_file_location("__main__", pipeline)
    ret = importlib.util.module_from_spec(spec)
    try:
        REQUIRE_FLAG = True
        spec.loader.exec_module(ret)
    except SystemExit:
        pass

    if not PIPELINES:
        logger.warning("  No pipelines found at %s" % pipeline)
        if PROCESSES:
            logger.warning("  But found processes: ")
            for process in PROCESSES:
                logger.warning("    %s", process)
        else:
            logger.error("No pipelines nor processes found.")
            sys.exit(1)


def install_process(proc, failed_tools, bindir):
    """Install failed tools for a process"""
    logger.install('  Installing failed tools')

    for tool, info in failed_tools.items():
        if 'install' not in info:
            logger.warning('    - %s: No `install` found in the annotation.',
                           tool)
            continue

        install = proc.template(info['install'], **proc.envs).render(
            dict(proc=proc, args=proc.args, bindir=bindir))
        installcmd = cmdy.bash(c=install, _raise=False)
        if installcmd.rc == 0:
            logger.info('    - %s: INSTALLED', tool)
        else:
            logger.error('    - %s: FAILED', tool)


def validate_process(proc, install=None, post=False):
    """Validate tools for a process"""
    if not post:
        logger.process(proc)
    if not proc.config.annotate:  # pragma: no cover
        logger.warning("  No annotations found, skip.")
        return
    reqanno = proc.config.annotate.section('requires', toml.loads)
    if not reqanno:
        logger.warning("  No `requires` in annotation, skip.")
        return

    failed_tools = OrderedDiot()
    logger['re-vali' if post else 'valid'](
        '  Post-install validating ...' if post else '  Validating ...')
    for tool, info in reqanno.items():
        if 'validate' not in info:
            logger.error('    - %s: No `validate` found in the annotation.',
                         tool)
            continue
        when = info.get('when', 'true')
        when = proc.template(when, **proc.envs).render(
            dict(proc=proc, args=proc.args))
        whencmd = cmdy.bash(c=when, _raise=False)
        if whencmd.rc != 0:
            logger.info("    - %s: condition (when) not met, skip.", tool)
            continue
        validate = proc.template(info['validate'], **proc.envs).render(
            dict(proc=proc, args=proc.args))
        validcmd = cmdy.bash(c=validate, _raise=False)
        if validcmd.rc != 0:
            logger['warning' if not post else 'error']('    - %s: FAILED',
                                                       tool)
            failed_tools[tool] = info
        else:
            logger.info('    - %s: PASSED', tool)

    if install and failed_tools:
        install_process(proc, failed_tools, bindir=install)
        validate_process(proc, install=None, post=True)


@hookimpl
def pyppl_prerun(ppl):  # pylint: disable=inconsistent-return-statements
    """Stop pipeline from running"""
    if REQUIRE_FLAG:
        logger.warning("Pipeline was prevented from running by pyppl_require.")
        return False


@hookimpl
def logger_init(logger): # pylint: disable=redefined-outer-name
    """Add log levels"""
    logger.add_level('require', 'title')
    logger.add_level('Valid')
    logger.add_level('Install')
    logger.add_level('Re-vali')


@hookimpl
def cli_addcmd(commands):
    """Add command to pyppl."""
    commands.require = __doc__
    params = commands.require
    params._desc = 'Process requirement manager'
    params.pipe.required = True
    params.pipe.desc = 'The pipeline script.'
    params.p = params.pipe
    params.install.desc = [
        'Install the requirements. ',
        'You can specify a directory (default: $HOME/bin) '
        'to install the requirements.'
    ]
    params.install.callback = lambda opt: (
        opt.set_value(Path.home().joinpath('bin'))
        if opt.value is True
        else opt.set_value(Path(opt.value))
        if opt.value
        else None
    )


@hookimpl
def cli_execcmd(command, opts):
    """Execute the command"""
    if command == 'require':
        load_pipeline(opts.p)
        if PIPELINES:
            for name, pipeline in PIPELINES.items():
                logger.require('-' * 80)
                logger.require('Processing pipeline: %s', name)
                logger.require('-' * 80)
                for process in pipeline.procs:
                    validate_process(process, install=opts.install)
        else:
            for process in PROCESSES:
                validate_process(process, install=opts.install)
