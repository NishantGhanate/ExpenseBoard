from nicegui import ui

BASE_THEME_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@100;300;400;700;900&display=swap');
:root {
    --q-primary: #6366f1;
}
html, body {
    margin: 0;
    padding: 0;
    font-family: 'Outfit', sans-serif;
    background-color: #020617;
    background-image: 
        radial-gradient(at 0% 0%, rgba(30, 58, 138, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(79, 70, 229, 0.1) 0px, transparent 50%);
    color: #f8fafc;
    min-height: 100vh;
    overflow-y: auto;
    scrollbar-width: none; /* Firefox */
    -ms-overflow-style: none;  /* IE and Edge */
}
html::-webkit-scrollbar, body::-webkit-scrollbar, *::-webkit-scrollbar {
    display: none !important; /* Chrome, Safari and Opera */
}
.glass {
    background: rgba(15, 23, 42, 0.6) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
}
.glass-card {
    background: rgba(15, 23, 42, 0.6) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    transition: all 0.3s ease;
}
.glass-card:hover {
    background: rgba(15, 23, 42, 0.8) !important;
    border: 1px solid rgba(99, 102, 241, 0.3) !important;
    transform: translateY(-2px);
}
.neon-text {
    text-shadow: 0 0 10px rgba(99, 102, 241, 0.5);
}
.property-panel .q-field__native, .property-panel .q-field__label {
    color: #e2e8f0 !important;
}
.property-panel .q-field--outlined .q-field__control:before {
    border-color: rgba(255, 255, 255, 0.1) !important;
}
.property-panel .q-field--focused .q-field__control:after {
    border-color: #6366f1 !important;
}
.stealth-table {
    background: transparent !important;
}
.stealth-table thead tr th {
    color: #94a3b8 !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    border-bottom: 2px solid rgba(99, 102, 241, 0.2) !important;
}
.stealth-table tbody tr {
    transition: background 0.2s;
}
.stealth-table tbody tr:hover {
    background: rgba(99, 102, 241, 0.05) !important;
}
"""

def apply_styles():
    ui.add_head_html(f'<style>{BASE_THEME_CSS}</style>')
