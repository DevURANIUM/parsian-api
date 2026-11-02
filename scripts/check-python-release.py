import os
import pathlib
import tomllib
import parsianapi
metadata=tomllib.loads(pathlib.Path('python/pyproject.toml').read_text())
version=metadata['project']['version']
assert metadata['project']['name']=='parsian-api'
assert version==parsianapi.__version__, 'Python version mismatch'
assert os.environ.get('RELEASE_VERSION')==version, 'Selected version must match python/pyproject.toml version'
print('Release metadata verified:',version)
