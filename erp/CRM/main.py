"""Local launcher for the CRM FastAPI application."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

SERVICE_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = SERVICE_ROOT.parent
SRC_ROOT = SERVICE_ROOT / "src"

workspace_root = str(WORKSPACE_ROOT)
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)


def _load_service_main() -> ModuleType:
    """Load `src/main.py` without requiring PYTHONPATH in local commands."""

    src_root = str(SRC_ROOT)
    if src_root not in sys.path:
        sys.path.insert(0, src_root)

    spec = importlib.util.spec_from_file_location("_crm_service_main", SRC_ROOT / "main.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load CRM/src/main.py")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_service_main = _load_service_main()
create_app = _service_main.create_app
app = _service_main.app


def main() -> None:
    """Run the CRM local development server."""

    import uvicorn

    uvicorn.run(
        "CRM.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[str(SERVICE_ROOT)],
    )


if __name__ == "__main__":
    main()
