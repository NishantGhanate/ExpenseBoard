"""
Entrypoint for the NiceGUI Rules App.

Usage:
    python run_ui.py                  # local dev
    docker-compose up rules-app       # Docker

Env vars (all optional, sensible defaults for both local and Docker):
    RULES_APP_HOST      - bind host       (default: 0.0.0.0)
    RULES_APP_PORT      - bind port       (default: 8085)
    RULES_APP_STORAGE   - NiceGUI storage path for persistent state
                          (default: ./ui_storage locally, /app/ui_storage in Docker)
    NICEGUI_SECRET      - cookie signing secret
"""

import logging
import os
import sys
from pathlib import Path

# ── 4. App imports (after sys.path is ready) ──────────────────────────────────
from app.ui.app_logic import RulesApp  # noqa: E402
from nicegui import app as nicegui_app  # noqa: E402
from nicegui import ui

# ── 1. Path setup — must happen before any app.* imports ─────────────────────
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ── 2. Settings ───────────────────────────────────────────────────────────────
HOST = os.getenv("RULES_APP_HOST", "0.0.0.0")
PORT = int(os.getenv("RULES_APP_PORT", "8085"))

# Default storage: /app/ui_storage inside Docker, ./ui_storage locally
_docker_path = "/app/ui_storage"
_local_path  = str(ROOT / "ui_storage")
_default_storage = _docker_path if Path("/app").is_dir() and os.access("/app", os.W_OK) else _local_path
STORAGE_PATH = Path(os.getenv("RULES_APP_STORAGE", _default_storage))
STORAGE_PATH.mkdir(parents=True, exist_ok=True)

# ── 3. Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("run_ui")



def main() -> None:
    logger.info("═" * 60)
    logger.info("  ExpenseBoard · Rules & Ledger UI")
    logger.info(f"  Binding  : http://{HOST}:{PORT}")
    logger.info(f"  Storage  : {STORAGE_PATH}")
    logger.info("═" * 60)

    # Persistent NiceGUI storage (survives container restarts)
    nicegui_app.storage.path = STORAGE_PATH

    # Health-check endpoint polled by Docker HEALTHCHECK
    @ui.page("/healthz")
    def health():
        ui.label("ok")

    # Main page — each browser tab gets its own RulesApp instance
    @ui.page("/")
    def index():
        rules_app = RulesApp()
        rules_app.load_data()
        rules_app.build_ui()

    ui.run(
        host=HOST,
        port=PORT,
        title="ExpenseBoard · Intelligence Engine",
        dark=True,
        favicon="🚀",
        storage_secret=os.getenv("NICEGUI_SECRET", "expenseboard-secret-change-me"),
        reload=False,   # must be False inside Docker — no file watching
        show=False,     # never open a browser tab in headless mode
    )


if __name__ == "__main__":
    main()
