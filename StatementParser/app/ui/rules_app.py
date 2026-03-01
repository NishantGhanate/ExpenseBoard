"""
Legacy local-dev entrypoint for the NiceGUI Rules App.

For Docker use `run_ui.py` at the project root instead.
"""
import sys
from pathlib import Path

# Allow running directly: python app/ui/rules_app.py
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if __name__ in {"__main__", "__mp_main__"}:
    # Delegate to the canonical entrypoint
    import run_ui
    run_ui.main()
