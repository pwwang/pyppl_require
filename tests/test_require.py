import pytest
import cmdy
import sys
from os import environ
from pathlib import Path
from pyppl.utils import chmod_x

@pytest.fixture
def pyppl():
	return cmdy.pyppl(_exe=Path(__file__).parent.joinpath('pyppl'),
				 _sub=True, _raise=False)
procs = Path(__file__).parent.joinpath('procs.py')
pipeline = Path(__file__).parent.joinpath('pipeline.py')
none = Path(__file__).parent.joinpath('none.py')

def test_procs(pyppl):
	err = pyppl.require(p = procs).stderr
	assert 'No pipelines found' in err
	assert 'But found processes:' in err
	assert "Proc(name='pProcess1.notag')" in err
	assert "Validating ..." in err
	assert 'tool1: FAILED' in err
	assert 'No `requires` in annotation, skip.' in err
	assert '- tool1: No `validate` found in the annotation.' in err
	assert '- tool2: condition (when) not met, skip.' in err
	assert 'tool2: PASSED' in err

def test_script_in_path(pyppl):
	chmod_x(procs)
	err = pyppl.require(p = 'procs.py', install = True,
		_env = {'PATH': procs.parent.resolve().as_posix() + ':' + environ['PATH']}).stderr
	assert 'No pipelines found' in err
	assert 'But found processes:' in err
	assert "Proc(name='pProcess1.notag')" in err
	assert "Validating ..." in err
	assert 'tool1: FAILED' in err
	assert '- tool2: FAILED' in err
	assert 'tool1: No `install` found in the annotation.' in err

def test_pipeline_not_found(pyppl):
	err = pyppl.require(p = '__nonexist/_file__').stderr
	assert 'Pipeline script does not exist:' in err

def test_none(pyppl):
	err = pyppl.require(p = none).stderr
	assert 'No pipelines nor processes found.' in err

def test_pipeline(pyppl):
	c = pyppl.require(p = pipeline)
	assert 'Pipeline was prevented from running by pyppl_require.' in c.stderr
	# unrelated procs are not loaded.
	assert 'pProcessNoValid' not in c.stderr

def test_noclimode(pyppl):
	"""Not in cli mode, pipeline should be running"""
	c = cmdy.python(pipeline, _exe = sys.executable, _raise = False)
	assert 'Pipeline was prevented from running by pyppl_require.' not in c.stderr
