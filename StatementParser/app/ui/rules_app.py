from nicegui import ui
from app.ui.app_logic import RulesApp
import sys

def main():
    try:
        print("Starting Rules App...")
        app = RulesApp()
        print("Loading data...")
        app.load_data()
        print("Building UI...")
        app.build_ui()
        print("Starting NiceGUI server...")
        ui.run(
            title='ExpenseBoard | Intelligence Engine',
            host='0.0.0.0',  # Bind to all interfaces for Docker
            port=8085,
            dark=True,
            favicon='🚀',
            reload=False  # Disable reload in Docker
        )
    except Exception as e:
        print(f"ERROR: Failed to start Rules App: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ in {"__main__", "__mp_main__"}:
    main()
