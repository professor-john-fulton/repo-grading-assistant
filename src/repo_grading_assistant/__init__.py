from __future__ import annotations

from importlib import util as importlib_util
from pathlib import Path


def _load_version() -> str:
	try:
		from VERSION import __version__
		return __version__
	except ModuleNotFoundError:
		version_path = Path(__file__).resolve().parents[2] / "VERSION.py"
		if not version_path.exists():
			return "unknown"

		spec = importlib_util.spec_from_file_location("VERSION", version_path)
		if spec is None or spec.loader is None:
			return "unknown"

		module = importlib_util.module_from_spec(spec)
		spec.loader.exec_module(module)
		return getattr(module, "__version__", "unknown")


__version__ = _load_version()
