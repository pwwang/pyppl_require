import pytest
import cmdy
import sys
from os import environ
from pathlib import Path
from pyppl.utils import chmod_x

cmd = cmdy.pyppl.bake(Path(__file__).parent.joinpath('pyppl'), 'require', _exe = sys.executable, _raise = False)
procs = Path(__file__).parent.joinpath('procs.py')
pipeline = Path(__file__).parent.joinpath('pipeline.py')
none = Path(__file__).parent.joinpath('none.py')

def test_procs():
	err = cmd(p = procs).stderr
	assert 'No pipelines found' in err
	assert 'But found processes:' in err
	assert "Proc(name='pProcess1.notag')" in err
	assert "Validating ..." in err
	assert 'tool1: FAILED' in err
	assert 'No `requires` in annotation, skip.' in err
	assert '- tool1: No `validate` found in the annotation.' in err
	assert '- tool2: condition (when) not met, skip.' in err
	assert 'tool2: PASSED' in err

def test_script_in_path():
	chmod_x(procs)
	err = cmd(p = 'procs.py', install = True,
		_env = {'PATH': procs.parent.resolve().as_posix() + ':' + environ['PATH']}).stderr
	assert 'No pipelines found' in err
	assert 'But found processes:' in err
	assert "Proc(name='pProcess1.notag')" in err
	assert "Validating ..." in err
	assert 'tool1: FAILED' in err
	assert '- tool2: FAILED' in err
	assert 'tool1: No `install` found in the annotation.' in err

def test_pipeline_not_found():
	err = cmd(p = '__nonexist/_file__').stderr
	assert 'Pipeline script does not exist:' in err

def test_none():
	err = cmd(p = none).stderr
	assert 'No pipelines nor processes found.' in err

def test_pipeline():
	err = cmd(p = pipeline).stderr
	assert 'Pipeline was prevented from running by pyppl_require.' in err
	# unrelated procs are not loaded.
	assert 'pProcessNoValid' not in err
