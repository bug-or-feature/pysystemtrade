from importlib.util import find_spec
from pathlib import Path

module_spec = find_spec(__name__)
path = Path(module_spec.origin)

PYSYS_PROJECT_DIR = path.parent.parent
