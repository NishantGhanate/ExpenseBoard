"""
Entrypoint for the NiceGUI Rules App in Docker.

Usage:
    python run_ui.py

Env vars (all optional, fall back to defaults):
    RULES_APP_HOST      - bind host       (default: 0.0.0.0)
    RULES_APP_PORT      - bind port       (default: 8085)
    RULES_APP_STORAGE   - NiceGUI storage path for persistent state (default: /app/ui_storage)
    NICEGUI_SECRET      - cookie signing secret (default: expenseboard-secret-change-me)
"""

import logging
import os
import sys
from pathlib import Path

# ── App imports (after path is set) ──────────────────────────────────────────
from app.ui.app_logic import RulesApp  # noqa: E402
from nicegui import app as nicegui_app  # noqa: E402
from nicegui import ui

# ── Ensure project root is on sys.path before any app.* imports ──────────────
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ── Settings (read from env so Docker compose can override them) ─────────────
HOST = os.getenv("RULES_APP_HOST", "0.0.0.0")
PORT = int(os.getenv("RULES_APP_PORT", "8085"))
STORAGE_PATH = Path(os.getenv("RULES_APP_STORAGE", "/app/ui_storage"))
STORAGE_PATH.mkdir(parents=True, exist_ok=True)

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

    # ── Persistent NiceGUI storage (survives container restarts) ─────────────
    nicegui_app.storage.path = STORAGE_PATH

    # ── Health-check endpoint used by Docker HEALTHCHECK ─────────────────────
    @ui.page("/healthz")
    def health():
        ui.label("ok")

    # ── Main page — each browser tab gets a fresh RulesApp instance ──────────
    @ui.page("/")
    def index():
        rules_app = RulesApp()
        rules_app.load_data()
        rules_app.build_ui()

    logger.info("Starting NiceGUI server …")
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
