"""
Tests for the reductus.reduce Python scripting API.
"""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path for regression module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_reduce_module_import():
    """Test that the reduce module can be imported."""
    from reductus import reduce
    assert hasattr(reduce, 'load_template')
    assert hasattr(reduce, 'run')
    assert hasattr(reduce, 'Template')
    assert hasattr(reduce, 'ReductionResult')


def test_template_load():
    """Test loading a template from file."""
    from reductus import reduce

    template_path = 'reductus/reflred/templates/ncnr.refl.unpolarized.json'
    template = reduce.load_template(template_path)

    assert template is not None
    assert hasattr(template, 'template_def')
    assert 'modules' in template.template_def
    assert len(template.template_def['modules']) > 0


def test_template_from_dict():
    """Test creating a template from a dictionary."""
    from reductus import reduce

    template_def = {
        'name': 'test',
        'modules': [
            {'module': 'test.module', 'config': {}}
        ],
        'wires': [],
    }

    template = reduce.Template.from_dict(template_def)
    assert template.template_def == template_def


def test_find_loader_nodes():
    """Test finding loader nodes in a template."""
    from reductus import reduce
    from reductus.dataflow.configure import load_config, apply_config

    # Initialize to load instruments
    config = load_config(name='config', fallback=True)
    apply_config(user_config=config)

    template_path = 'reductus/reflred/templates/ncnr.refl.unpolarized.json'
    template_def = json.load(open(template_path))

    loaders = reduce._find_loader_nodes(template_def)

    # The unpolarized template should have multiple loader nodes
    # (one for specular, background+, background-, and intensity)
    assert len(loaders) > 0
    assert all(isinstance(idx, int) for idx in loaders)


def test_path_to_fileinfo():
    """Test converting filesystem paths to fileinfo dicts."""
    from reductus import reduce
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test file
        test_file = os.path.join(tmpdir, 'test.dat')
        with open(test_file, 'w') as f:
            f.write('test')

        # Convert to fileinfo
        fileinfos = reduce._path_to_fileinfo(test_file)

        assert len(fileinfos) == 1
        assert fileinfos[0]['source'] == 'local'
        assert fileinfos[0]['path'] == test_file.replace('\\', '/')
        assert fileinfos[0]['mtime'] > 0


def test_path_to_fileinfo_glob():
    """Test glob expansion in _path_to_fileinfo."""
    from reductus import reduce
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create multiple test files
        for i in range(3):
            test_file = os.path.join(tmpdir, f'test{i}.dat')
            with open(test_file, 'w') as f:
                f.write(f'test{i}')

        # Glob for all .dat files
        pattern = os.path.join(tmpdir, '*.dat')
        fileinfos = reduce._path_to_fileinfo(pattern)

        assert len(fileinfos) == 3
        for info in fileinfos:
            assert info['source'] == 'local'
            assert info['path'].endswith('.dat')


def test_reduction_result_save():
    """Test saving reduction results."""
    from reductus import reduce
    from reductus.dataflow.core import Bundle, DataType

    # Create a mock bundle
    datatype = DataType('test.type', object)

    # Create a simple mock object with a name attribute
    class MockData:
        def __init__(self, name):
            self.name = name

        def __str__(self):
            return f"Mock data: {self.name}"

    mock_value = MockData("test_data")
    bundle = Bundle(datatype=datatype, values=[mock_value])

    # Create result and save
    result = reduce.ReductionResult(bundle)

    with tempfile.TemporaryDirectory() as tmpdir:
        result.save(tmpdir)

        # Check that files were created
        output_files = os.listdir(tmpdir)
        assert len(output_files) > 0
        assert any(f.endswith('.dat') for f in output_files)


def test_regression_file_replay():
    """Test running a reduction using a regression file template."""
    from reductus import reduce

    # Pick the first regression file
    regression_file = 'tests/regression_files/5K_3T_aYIG_SiO2_FC56935.refl'

    if not os.path.exists(regression_file):
        # Skip if regression file not available
        return

    # Load template data from regression file
    with open(regression_file, 'r') as f:
        first_line = f.readline()

    # Parse template data from first line
    import re
    TEMPLATE = re.compile(r"^(#|//) *([\"']?template(_data)?[\"']?)? *[:=]? *\{")
    template_data = json.loads(TEMPLATE.sub('{', first_line))

    # Extract template, config, and target
    template_def = template_data['template']
    config = template_data.get('config', {})
    target_node = template_data.get('node', -1)
    target_terminal = template_data.get('terminal', 'output')

    # Create template and try to run it
    template = reduce.Template.from_dict(template_def)

    # The regression file already has the filelist configured,
    # so we can run it directly with the config
    from reductus.dataflow.configure import apply_config
    from reductus.dataflow.core import Template as CoreTemplate
    from reductus.dataflow.calc import process_template

    # Initialize
    first_module = template_def['modules'][0]['module']
    instrument_id = first_module.split('.')[1]
    apply_config(user_overrides={"instruments": [instrument_id], "cache": None})

    # Run the template
    core_template = CoreTemplate(**template_def)
    bundle = process_template(core_template, config, target=(target_node, target_terminal))

    # Result should have data
    assert bundle is not None
    assert hasattr(bundle, 'values')
    assert len(bundle.values) > 0


if __name__ == '__main__':
    import sys

    # Run tests manually
    test_functions = [
        test_reduce_module_import,
        test_template_load,
        test_template_from_dict,
        test_find_loader_nodes,
        test_path_to_fileinfo,
        test_path_to_fileinfo_glob,
        test_reduction_result_save,
        test_regression_file_replay,
    ]

    for test_func in test_functions:
        try:
            test_func()
            print(f"PASS: {test_func.__name__}")
        except Exception as e:
            print(f"FAIL: {test_func.__name__}: {e}")
            import traceback
            traceback.print_exc()
