import re
from typing import Optional, Any, List, Dict
from nicegui import ui
from app.ui.db_manager import (
    Rule, fetch_rules, fetch_rule_by_id, save_rule, delete_rule, 
    toggle_rule_active, fetch_sample_transactions, fetch_categories, 
    fetch_tags, fetch_payment_methods, fetch_transaction_types, 
    fetch_goals, fetch_banks, fetch_users, save_category, delete_category,
    fetch_transactions, update_transaction_field, process_transactions_with_rules,
    update_transactions_bulk
)
from app.ui.styles import apply_styles

# Import rule engine for proper validation
try:
    from app.rule_engine.parser import parse, try_parse
    from app.rule_engine.evaluator import RuleEvaluator
    USE_FULL_PARSER = True
except ImportError:
    USE_FULL_PARSER = False

class DSLValidator:
    """DSL validator - uses full parser if available, else simple regex."""
    ASSIGNMENTS = {'category_id', 'tag_id', 'type_id', 'payment_method_id', 'goal_id'}

    @classmethod
    def validate(cls, dsl_text: str) -> tuple[bool, str]:
        if not dsl_text or not dsl_text.strip():
            return False, "DSL text is required"
        if USE_FULL_PARSER:
            result, error = try_parse(dsl_text)
            if error: return False, f"❌ {error}"
            return True, "✅ Valid syntax"
        
        text = dsl_text.strip()
        if not text.lower().startswith('rule'): return False, "Must start with 'rule'"
        if not text.endswith(';'): return False, "Must end with ';'"
        if 'where' not in text.lower(): return False, "Missing 'where'"
        if 'assign' not in text.lower(): return False, "Missing 'assign'"
        if not re.search(r'rule\s+"([^"]+)"', text, re.IGNORECASE): return False, "Rule name must be in quotes"
        if not any(a in text.lower() for a in cls.ASSIGNMENTS): return False, "Missing assignment"
        if text.count('"') % 2 != 0: return False, "Unbalanced quotes"
        return True, "✅ Valid syntax"

DSL_HELP = """
## Rule Syntax
```
rule "Rule Name" where <conditions> assign <assignments> priority <number>;
```

## Transaction Fields
| Field | Description |
|-------|-------------|
| `description` | Transaction narration |
| `entity_name` | Payee/receiver name |
| `amount` | Transaction amount |
| `transaction_date` | Date of transaction (YYYY-MM-DD) |
| `bank_account_id` | Unique ID of the bank account |
| `type` | "credit" or "debit" |

## Operators
- `eq`, `neq`: Equal, Not Equal
- `gt`, `lt`, `gte`, `lte`: Greater/Less than (amounts/dates)
- `between`: Range (e.g. `amount:between:"100":"500"`)
- `con`, `noc`: Contains, Not Contains
- `sw`, `ew`: Starts with, Ends with
- `in`, `nin`: In list, Not in list (e.g. `category_id:in:1,2,3`)
- `null`, `nnull`: Is Null, Is Not Null
- `regex`: Regular expression

## Examples
```
rule "Rent Payment" where description:con:"RENT" assign category_id:2 priority 10;
rule "Salary Credit" where amount:gt:"50000" and type:eq:"credit" assign category_id:1 priority 1;
rule "Shopping" where entity_name:in:"Amazon","Flipkart" assign category_id:4;
```
"""

class RulesApp:
    def __init__(self):
        self.current_user_id = 1
        self.rules = []
        self.categories = []
        self.tags = []
        self.payment_methods = []
        self.transaction_types = []
        self.goals = []
        self.users = []
        self.bank_accounts = []
        self.editing_rule_id = None
        self.rule_creation_mode = "raw"
        self.search_text = ""
        self.page = 1
        self.page_size = 10
        self.active_filter = None
        self.category_filter = None

        # UI references
        self.rules_container = None
        self.name_input = None
        self.dsl_input = None
        self.priority_input = None
        self.active_switch = None
        self.validation_label = None
        self.form_title = None
        self.save_button = None
        self.db_status_label = None
        self.dashboard_container = None
        self.txn_search_text = ""
        self.txn_uncategorized_only = False
        self.txn_date_from = ""
        self.txn_date_to = ""
        
        # Initialize data attributes to prevent crashes
        self.rules = []
        self.categories = []
        self.tags = []
        self.payment_methods = []
        self.transaction_types = []
        self.goals = []
        self.users = []
        self.bank_accounts = []
        self.transactions = []

    def load_data(self):
        try:
            self.rules = fetch_rules(self.current_user_id)
            self.categories = fetch_categories()
            self.tags = fetch_tags()
            self.payment_methods = fetch_payment_methods()
            self.transaction_types = fetch_transaction_types()
            self.goals = fetch_goals()
            self.users = fetch_users()
            self.bank_accounts = fetch_banks(self.current_user_id)
            self.transactions = fetch_transactions(self.current_user_id)
        except Exception as e:
            ui.notify(f"Error loading data: {e}", type="negative")

    def on_dsl_change(self, e):
        val = e.value if hasattr(e, 'value') else e.get('value') if isinstance(e, dict) else str(e)
        is_valid, msg = DSLValidator.validate(val)
        if self.validation_label:
            self.validation_label.text = msg
            self.validation_label.classes(remove='text-green-600 text-red-600')
            self.validation_label.classes(add='text-green-600' if is_valid else 'text-red-600')

    def reset_form(self):
        self.editing_rule_id = None
        if self.name_input: self.name_input.value = ""
        if self.dsl_input: self.dsl_input.value = ""
        if self.priority_input: self.priority_input.value = 100
        if self.active_switch: self.active_switch.value = True
        if self.validation_label: self.validation_label.text = ""
        if self.form_title: self.form_title.text = "Create New Rule"
        if self.save_button: self.save_button.text = "Create Rule"

    async def duplicate_rule(self, row: dict):
        """Duplicate a rule into the form from table row data."""
        if self.name_input: self.name_input.value = f"{row['name']} (copy)"
        if self.dsl_input:
            # Table row uses 'dsl', DB rule uses 'dsl_text'
            dsl_val = row.get('dsl') or row.get('dsl_text') or ""
            dsl = re.sub(r'rule\s+"([^"]+)"', f'rule "{row["name"]} (copy)"', dsl_val, flags=re.IGNORECASE)
            self.dsl_input.value = dsl
        if self.priority_input: self.priority_input.value = row['priority']
        if self.active_switch: self.active_switch.value = True
        if self.form_title: self.form_title.text = "Create New Rule (from copy)"
        if self.save_button: self.save_button.text = "Create Rule"
        self.editing_rule_id = None
        self.on_dsl_change({'value': self.dsl_input.value if self.dsl_input else ""})

    def show_dsl(self, name: str, dsl: str):
        with ui.dialog() as d, ui.card().classes('w-[700px] glass p-6 rounded-3xl'):
            ui.label(f"Rule: {name}").classes('text-lg font-bold text-white mb-4')
            ui.code(dsl, language='sql').classes('w-full bg-slate-900/50 p-4 rounded-xl')
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Copy', on_click=lambda: (ui.clipboard.write(dsl), ui.notify('Copied!'))).props('flat color=indigo-400')
                ui.button('Close', on_click=d.close).props('flat color=slate-400')
        d.open()

    def edit_rule(self, rule_id: int):
        rule = fetch_rule_by_id(rule_id)
        if rule:
            self.editing_rule_id = rule_id
            if self.name_input: self.name_input.value = rule['name']
            if self.dsl_input: self.dsl_input.value = rule['dsl_text']
            if self.priority_input: self.priority_input.value = rule['priority']
            if self.active_switch: self.active_switch.value = rule['is_active']
            if self.form_title: self.form_title.text = f"Edit: {rule['name']}"
            if self.save_button: self.save_button.text = "Update Rule"
            self.on_dsl_change({'value': rule['dsl_text']})

    async def save_rule_handler(self):
        name = self.name_input.value.strip() if self.name_input else ""
        dsl_text = self.dsl_input.value.strip() if self.dsl_input else ""
        priority = int(self.priority_input.value) if self.priority_input else 100
        is_active = self.active_switch.value if self.active_switch else True

        if not name:
            ui.notify("Rule name is required", type="warning")
            return
        if not dsl_text and self.rule_creation_mode == 'guided':
            self.generate_dsl_from_guided()
            dsl_text = self.dsl_input.value

        is_valid, error = DSLValidator.validate(dsl_text)
        if not is_valid:
            ui.notify(f"Invalid DSL: {error}", type="negative")
            return

        try:
            rule = Rule(id=self.editing_rule_id, name=name, dsl_text=dsl_text, priority=priority, user_id=self.current_user_id, is_active=is_active)
            save_rule(rule)
            action = "updated" if self.editing_rule_id else "created"
            ui.notify(f"Rule '{name}' {action}!", type="positive")
            self.refresh_all_ui()
            self.reset_form()
        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")

    async def delete_rule_handler(self, rule_id: int, rule_name: str):
        with ui.dialog() as dialog, ui.card():
            ui.label(f"Delete '{rule_name}'?").classes('text-lg font-bold')
            ui.label("This cannot be undone.").classes('text-gray-600')
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                async def confirm():
                    delete_rule(rule_id)
                    ui.notify(f"Deleted '{rule_name}'", type="positive")
                    dialog.close()
                    self.refresh_all_ui()
                    if self.editing_rule_id == rule_id: self.reset_form()
                ui.button('Delete', on_click=confirm).props('color=negative')
        dialog.open()

    def refresh_all_ui(self):
        self.load_data()
        self.render_dashboard()
        self.render_form_inputs()
        self.refresh_rules_list()
        self.refresh_transactions_table()

    def refresh_rules_list(self):
        if self.rules_container:
            self.rules_container.clear()
            with self.rules_container:
                self.render_rules_list()

    def get_name(self, lookup, id_val: Optional[int], key: str = 'name') -> str:
        if id_val is None: return "-"
        for item in lookup:
            if item['id'] == id_val: return item[key]
        return f"ID:{id_val}"

    def parse_assignments(self, dsl: str) -> dict:
        if USE_FULL_PARSER:
            try:
                rule = parse(dsl)
                return {
                    'category_id': rule.assignment.category_id,
                    'tag_id': rule.assignment.tag_id,
                    'type_id': rule.assignment.type_id,
                    'payment_method_id': rule.assignment.payment_method_id,
                    'goal_id': rule.assignment.goal_id,
                }
            except: pass
        result = {}
        for field in ['category_id', 'tag_id', 'type_id', 'payment_method_id', 'goal_id']:
            match = re.search(rf'{field}:(\d+)', dsl, re.IGNORECASE)
            if match: result[field] = int(match.group(1))
        return result

    def render_rules_list(self):
        filtered_rules = self.rules
        if self.search_text:
            s = self.search_text.lower()
            filtered_rules = [r for r in filtered_rules if s in r['name'].lower() or s in r['dsl_text'].lower()]
        if self.active_filter is not None:
            filtered_rules = [r for r in filtered_rules if r['is_active'] == self.active_filter]
        if self.category_filter is not None:
            new_filtered = []
            for r in filtered_rules:
                assigns = self.parse_assignments(r['dsl_text'])
                if assigns.get('category_id') == self.category_filter:
                    new_filtered.append(r)
            filtered_rules = new_filtered
            
        rows = []
        for r in filtered_rules:
            assigns = self.parse_assignments(r['dsl_text'])
            rows.append({
                'id': r['id'], 'name': r['name'], 'priority': r['priority'], 
                'is_active': r['is_active'], 'category': self.get_name(self.categories, assigns.get('category_id')),
                'tag': self.get_name(self.tags, assigns.get('tag_id')),
                'type': self.get_name(self.transaction_types, assigns.get('type_id')),
                'method': self.get_name(self.payment_methods, assigns.get('payment_method_id')),
                'dsl': r['dsl_text']
            })

        columns = [
            {'name': 'priority', 'label': 'Prio', 'field': 'priority', 'sortable': True, 'align': 'left'},
            {'name': 'name', 'label': 'Rule Name', 'field': 'name', 'sortable': True, 'align': 'left'},
            {'name': 'category', 'label': 'Category', 'field': 'category', 'sortable': True},
            {'name': 'method', 'label': 'Method', 'field': 'method', 'sortable': True},
            {'name': 'is_active', 'label': 'Active', 'field': 'is_active'},
            {'name': 'actions', 'label': 'Actions', 'field': 'id'},
        ]

        with ui.table(columns=columns, rows=rows, pagination=10, selection='multiple').classes('w-full stealth-table text-slate-300 border-none') as table:
            self.rules_table = table
            table.add_slot('header', r'''<q-tr :props="props"><q-th v-for="col in props.cols" :key="col.name" :props="props" class="text-indigo-400 font-black uppercase tracking-[0.2em] text-[10px]">{{ col.label }}</q-th></q-tr>''')
            table.add_slot('body-cell-priority', r'''<q-td :props="props"><span class="px-2 py-1 bg-indigo-500/10 text-indigo-400 rounded-lg text-[10px] font-black tracking-widest border border-indigo-500/20">{{ props.value }}</span></q-td>''')
            table.add_slot('body-cell-name', r'''<q-td :props="props"><div class="text-white font-bold tracking-tight">{{ props.value }}</div><div class="text-[9px] text-slate-500 font-mono truncate max-w-[200px]">{{ props.row.dsl }}</div></q-td>''')
            table.add_slot('body-cell-is_active', r'''<q-td :props="props"><div :class="props.value ? 'bg-emerald-400/10 text-emerald-400 cursor-pointer hover:bg-emerald-400/20' : 'bg-slate-700/30 text-slate-500 cursor-pointer hover:bg-slate-700/50'" class="inline-block px-3 py-1 rounded-full text-[9px] font-black tracking-widest uppercase border border-white/5" @click="$parent.$emit('toggle', props.row.id, !props.value)">{{ props.value ? 'Active' : 'Standby' }}</div></q-td>''')
            table.add_slot('body-cell-actions', r'''<q-td :props="props"><q-btn flat round dense icon="visibility" color="slate-400" @click="$parent.$emit('view', props.row.name, props.row.dsl)" class="hover:bg-white/5" /><q-btn flat round dense icon="edit" color="indigo-400" @click="$parent.$emit('edit', props.row.id)" class="hover:bg-indigo-400/10" /><q-btn flat round dense icon="content_copy" color="purple-400" @click="$parent.$emit('duplicate', props.row)" class="hover:bg-purple-400/10" /><q-btn flat round dense icon="delete" color="pink-400" @click="$parent.$emit('delete', props.row.id, props.row.name)" class="hover:bg-pink-400/10" /></q-td>''')

        table.on('view', lambda msg: self.show_dsl(msg.args[0], msg.args[1]))
        table.on('edit', lambda msg: self.edit_rule(msg.args))
        table.on('duplicate', lambda msg: self.duplicate_rule(msg.args))
        table.on('delete', lambda msg: self.delete_rule_handler(msg.args[0], msg.args[1]))
        table.on('toggle', lambda msg: (toggle_rule_active(msg.args[0], msg.args[1]), self.refresh_all_ui(), ui.notify(f"Rule status updated")))

    def render_dashboard(self):
        self.dashboard_container.clear()
        with self.dashboard_container:
            total_rules = len(self.rules)
            active_rules = sum(1 for r in self.rules if r['is_active'])
            total_categories = len(self.categories)

            with ui.row().classes('w-full gap-6 mb-4'):
                # Rules Stat
                with ui.card().classes('flex-1 glass-card p-6 rounded-3xl overflow-hidden relative cursor-pointer').on('click', lambda: self.set_filter('all', None)):
                    ui.element('div').classes('absolute -top-10 -right-10 w-40 h-40 bg-indigo-500/10 rounded-full blur-3xl')
                    with ui.column().classes('gap-0'):
                        ui.label('Total Rules').classes('text-[10px] font-black text-slate-500 uppercase tracking-[0.3em]')
                        with ui.row().classes('items-baseline gap-2 mt-2'):
                            ui.label(str(total_rules)).classes('text-5xl font-black text-white neon-text')
                            ui.label('entries').classes('text-xs text-slate-500')
                
                # Active Stat
                with ui.card().classes('flex-1 glass-card p-6 rounded-3xl overflow-hidden relative cursor-pointer').on('click', lambda: self.set_filter('active', True)):
                     ui.element('div').classes('absolute -top-10 -right-10 w-40 h-40 bg-emerald-500/10 rounded-full blur-3xl')
                     with ui.column().classes('gap-0 w-full'):
                        with ui.row().classes('w-full items-center justify-between'):
                            ui.label('Active Logic').classes('text-[10px] font-black text-slate-500 uppercase tracking-[0.3em]')
                            with ui.row().classes('gap-2'):
                                ui.button('APPLY RULES', on_click=self.handle_run_engine).props('flat dense color=indigo-400 icon=play_circle').classes('text-[10px] font-black tracking-widest hover:bg-indigo-500/10 px-2 rounded')
                                ui.button('MANAGE').on('click.stop', self.show_rule_manager).props('flat dense color=emerald-400').classes('text-[10px] font-black tracking-widest hover:bg-emerald-500/10 px-2 rounded')
                        with ui.row().classes('items-baseline gap-2 mt-2'):
                            ui.label(str(active_rules)).classes('text-5xl font-black text-emerald-400 neon-text')
                            ui.label(f"/ {total_rules - active_rules} standby").classes('text-xs text-slate-500 ml-1')
                            ui.badge(f"{int(active_rules/total_rules*100 if total_rules > 0 else 0)}%", color='emerald-500/20').props('outline text-color=emerald-400').classes('ml-auto')

                # Categories Stat
                with ui.card().classes('flex-1 glass-card p-6 rounded-3xl overflow-hidden relative cursor-pointer active:scale-95 transition-transform').on('click', self.show_category_summary):
                     ui.element('div').classes('absolute -top-10 -right-10 w-40 h-40 bg-purple-500/10 rounded-full blur-3xl')
                     with ui.column().classes('gap-0 w-full'):
                        with ui.row().classes('w-full items-center justify-between'):
                            ui.label('Total Classifications').classes('text-[10px] font-black text-slate-500 uppercase tracking-[0.3em]')
                            ui.button('MANAGE').on('click.stop', self.show_category_master).props('flat dense color=purple-400').classes('text-[10px] font-black tracking-widest hover:bg-purple-500/10 px-2 rounded')
                        with ui.row().classes('items-baseline gap-2 mt-2'):
                            ui.label(str(total_categories)).classes('text-5xl font-black text-purple-400 neon-text')
                            ui.label('categories').classes('text-xs text-slate-500')


    def render_targeting_panel(self):
        with ui.card().classes('w-full p-4 bg-indigo-500/5 border border-indigo-500/10 rounded-2xl'):
            with ui.row().classes('w-full items-center gap-2 mb-4'):
                ui.icon('gps_fixed', color='indigo-400', size='xs')
                ui.label('TARGETING SCOPE').classes('text-[9px] font-black text-indigo-400 tracking-[0.2em]')
            self.guided_bank = ui.select(label='Bank Account', options={b['id']: f"{b['number']} ({b['type']})" for b in self.bank_accounts}).props('dense outlined dark clearable color=indigo').classes('w-full mb-3')
            with ui.row().classes('w-full gap-2'):
                self.guided_start_date = ui.input(label='From Date').props('dense outlined dark color=indigo').classes('flex-1')
                with self.guided_start_date:
                    with ui.menu().props('no-parent-event') as m1: ui.date().bind_value(self.guided_start_date)
                    ui.button(icon='event', on_click=m1.open).props('flat dense').classes('cursor-pointer')
                self.guided_end_date = ui.input(label='To Date').props('dense outlined dark color=indigo').classes('flex-1')
                with self.guided_end_date:
                    with ui.menu().props('no-parent-event') as m2: ui.date().bind_value(self.guided_end_date)
                    ui.button(icon='event', on_click=m2.open).props('flat dense').classes('cursor-pointer')

    # Configuration for Guided Mode
    OPERATORS = {
        'eq': 'Equals', 'neq': 'Not Equals', 
        'gt': 'Greater Than', 'lt': 'Less Than', 
        'gte': 'Greater/Equal', 'lte': 'Less/Equal',
        'between': 'Between', 
        'con': 'Contains', 'noc': 'Not Contains', 
        'sw': 'Starts With', 'ew': 'Ends With', 
        'regex': 'Regex Pattern', 
        'in': 'In List', 'nin': 'Not In List', 
        'null': 'Is Empty', 'nnull': 'Not Empty'
    }

    FIELD_CONFIG = {
        'description': {'label': 'Description', 'ops': 'all'},
        'entity_name': {'label': 'Entity Name', 'ops': 'all'},
        'amount': {'label': 'Amount', 'ops': ['eq', 'neq', 'gt', 'lt', 'gte', 'lte', 'between']},
        'transaction_date': {'label': 'Date', 'ops': ['eq', 'neq', 'gt', 'lt', 'gte', 'lte', 'between']},
        'type': {'label': 'Type', 'ops': ['eq', 'neq']},
    }

    def render_form_inputs(self):
        self.dsl_input_container.clear()
        with self.dsl_input_container:
            if self.rule_creation_mode == "raw":
                with ui.column().classes('w-full gap-2'):
                    self.dsl_input = ui.textarea(label='DSL Rule', placeholder='rule "Name" where ... assign ... priority N;').classes('w-full h-48 font-mono text-sm').props('outlined dark color=indigo').on('change', self.on_dsl_change)
                    with ui.row().classes('w-full justify-end'):
                        ui.button('SYNC TARGETS', on_click=self.sync_targeting_to_raw).props('flat dense color=indigo').classes('text-[10px] font-black tracking-widest bg-white/5 px-4 rounded-lg hover:bg-indigo-500/10')
            else:
                with ui.card().classes('w-full p-4 bg-slate-800/40 border-dashed border-2 border-slate-700'):
                    ui.label('Logic Builder').classes('text-xs font-bold text-slate-500 mb-2 uppercase tracking-tighter')
                    
                    # Field Selection
                    with ui.row().classes('w-full gap-2 mb-2'):
                        field_opts = {k: v['label'] for k, v in self.FIELD_CONFIG.items()}
                        self.guided_field = ui.select(label='Field', options=field_opts, value='description', on_change=lambda: self.render_form_inputs()).props('dense outlined dark color=indigo').classes('flex-1')
                        
                        # Operator Selection based on field config
                        allowed_ops = self.FIELD_CONFIG[self.guided_field.value]['ops']
                        if allowed_ops == 'all':
                            op_opts = self.OPERATORS
                        else:
                            op_opts = {k: v for k, v in self.OPERATORS.items() if k in allowed_ops}
                        
                        default_op = 'con' if 'con' in op_opts else 'eq'
                        self.guided_op = ui.select(label='Operator', options=op_opts, value=default_op, on_change=lambda: self.render_form_inputs()).props('dense outlined dark color=indigo').classes('flex-1')

                    # Value Input(s) based on Operator
                    with ui.column().classes('w-full mb-4'):
                        op_val = self.guided_op.value
                        field_val = self.guided_field.value

                        if op_val in ('null', 'nnull'):
                            ui.label('No value needed').classes('text-[10px] text-slate-600 italic')
                        
                        elif op_val == 'between':
                            with ui.row().classes('w-full gap-2'):
                                if field_val == 'transaction_date':
                                    self._render_date_input('Start Date', 'guided_value')
                                    self._render_date_input('End Date', 'guided_value_high')
                                else:
                                    self.guided_value = ui.input(label='Low Value').props('dense outlined dark').classes('flex-1')
                                    self.guided_value_high = ui.input(label='High Value').props('dense outlined dark').classes('flex-1')
                        
                        elif field_val == 'transaction_date':
                            self._render_date_input('Date Value', 'guided_value', width='w-full')
                        
                        else:
                            self.guided_value = ui.input(label='Value').props('dense outlined dark color=indigo').classes('w-full')

                    ui.label('Assignments').classes('text-xs font-bold text-slate-500 mb-2 uppercase tracking-tighter')
                    self.guided_cat = ui.select(label='Category', options={c['id']: c['name'] for c in self.categories}).props('dense outlined dark clearable color=indigo').classes('w-full mb-2')
                    ui.button('GENERATE LOGIC', on_click=self.generate_dsl_from_guided).props('flat primary dense').classes('self-end text-indigo-300 font-bold')
                    self.dsl_input = ui.textarea().classes('hidden')

    def _render_date_input(self, label, attr_name, width='flex-1'):
        """Helper to render date dictionary inputs"""
        inp = ui.input(label=label).props('dense outlined dark color=indigo').classes(width)
        with inp:
            with ui.menu().props('no-parent-event') as menu: ui.date().bind_value(inp)
            ui.button(icon='event', on_click=menu.open).props('flat dense').classes('cursor-pointer')
        setattr(self, attr_name, inp)

    def sync_targeting_to_raw(self):
        dsl = self.dsl_input.value or f'rule "{self.name_input.value or "New Rule"}" where description:con:"" assign category_id:1;'
        match = re.search(r'rule\s+"([^"]+)"\s+where\s+(.*?)\s+assign', dsl, re.IGNORECASE)
        if not match: return
        name, condition = match.groups()
        conditions = [condition]
        if self.guided_bank.value and f'bank_account_id:eq:{self.guided_bank.value}' not in condition:
            conditions.append(f'bank_account_id:eq:{self.guided_bank.value}')
        if self.guided_start_date.value and self.guided_end_date.value:
            date_cond = f'transaction_date:between:"{self.guided_start_date.value}":"{self.guided_end_date.value}"'
            if date_cond not in condition: conditions.append(date_cond)
        new_dsl = dsl.replace(condition, " and ".join(conditions))
        self.dsl_input.value = new_dsl
        self.on_dsl_change({'value': new_dsl})

    def generate_dsl_from_guided(self):
        name = self.name_input.value or "New Rule"
        field = self.guided_field.value
        op = self.guided_op.value
        val = self.guided_value.value if hasattr(self, 'guided_value') else ""
        cat = self.guided_cat.value
        priority = int(self.priority_input.value)
        conditions = []
        
        if op == 'between':
            val_high = self.guided_value_high.value if hasattr(self, 'guided_value_high') else ""
            conditions.append(f'{field}:between:"{val}":"{val_high}"')
        elif op in ('null', 'nnull'): 
            conditions.append(f'{field}:{op}')
        else: 
            conditions.append(f'{field}:{op}:"{val}"')
            
        # Add targeting if present
        if self.guided_bank.value: 
            conditions.append(f'bank_account_id:eq:{self.guided_bank.value}')
        if self.guided_start_date.value and self.guided_end_date.value:
            conditions.append(f'transaction_date:between:"{self.guided_start_date.value}":"{self.guided_end_date.value}"')
            
        dsl = f'rule "{name}" where {" and ".join(conditions)}'
        if cat: 
            dsl += f' assign category_id:{cat}'
        dsl += f' priority {priority};'
        
        self.dsl_input.value = dsl
        self.on_dsl_change({'value': dsl})

    def show_category_summary(self):
        stats = {}
        for r in self.rules:
            cat_id = self.parse_assignments(r['dsl_text']).get('category_id')
            if cat_id: stats[cat_id] = stats.get(cat_id, 0) + 1
        with ui.dialog() as d, ui.card().classes('glass p-8 rounded-3xl w-[500px] border border-white/10'):
            ui.label('DISTRIBUTION').classes('text-[10px] font-black text-purple-400 tracking-[0.4em] mb-4')
            for cid, count in stats.items():
                name = self.get_name(self.categories, cid)
                with ui.row().classes('w-full items-center mb-2'):
                    ui.label(name).classes('text-white font-bold')
                    ui.space()
                    ui.label(str(count)).classes('text-purple-400 font-mono')
            ui.button('CLOSE', on_click=d.close).props('flat color=slate-400').classes('mt-8 self-end')
        d.open()

    def show_category_master(self):
        with ui.dialog() as d, ui.card().classes('glass p-8 rounded-3xl w-[700px] border border-white/10'):
            with ui.row().classes('w-full items-center justify-between mb-8'):
                ui.label('Category Master').classes('text-2xl font-bold text-white')
                ui.button('NEW CATEGORY', icon='add', on_click=lambda: self.add_category_form(on_success=d.close)).props('unelevated color=purple-500')
            with ui.column().classes('w-full gap-3 overflow-auto max-h-[500px]'):
                for cat in self.categories:
                    with ui.row().classes('w-full p-4 glass-card rounded-2xl items-center group'):
                        ui.element('div').style(f'background-color: {cat.get("color", "#6366f1")}').classes('w-3 h-10 rounded-full mr-4')
                        ui.label(cat['name']).classes('text-white font-bold text-lg')
                        ui.space()
                        with ui.row().classes('gap-2'):
                            ui.button(icon='edit', on_click=lambda c=cat: self.add_category_form(c, on_success=d.close)).props('flat round dense color=indigo-300')
                            ui.button(icon='delete', on_click=lambda cid=cat['id']: self.confirm_category_delete(cid, d.close)).props('flat round dense color=pink-400')
        d.open()

    def add_category_form(self, cat: dict = None, on_success=None):
        is_edit = cat is not None
        with ui.dialog() as d, ui.card().classes('glass p-8 rounded-3xl w-[400px] border border-white/10'):
            name_input = ui.input('Name', value=cat['name'] if is_edit else '').props('outlined dark').classes('w-full')
            type_select = ui.select(label='Type', options=['Credit', 'Debit', 'Neutral'], value=cat.get('type', 'Neutral') if is_edit else 'Neutral').props('outlined dark').classes('w-full')
            color_input = ui.input('Color', value=cat.get('color', '#6366f1') if is_edit else '#6366f1').props('outlined dark').classes('w-full')
            async def handle_save():
                if save_category({'id': cat['id'] if is_edit else None, 'name': name_input.value, 'type': type_select.value, 'color': color_input.value}):
                    d.close(); self.refresh_all_ui(); self.show_category_master()
            ui.button('SAVE', on_click=handle_save).props('color=indigo unelevated').classes('w-full mt-6')
        d.open()

    def show_rule_manager(self):
        with ui.dialog() as d, ui.card().classes('glass p-8 rounded-3xl w-[800px] border border-white/10'):
            with ui.row().classes('w-full items-center justify-between mb-8'):
                with ui.column().classes('gap-0'):
                    ui.label('Rule Management').classes('text-2xl font-bold text-white')
                    ui.label('Toggle rules between Active and Inactive states').classes('text-xs text-slate-500')
                ui.button('CLOSE', on_click=d.close).props('flat color=slate-400').classes('hover:bg-white/5')
            
            with ui.column().classes('w-full gap-3 overflow-auto max-h-[600px] pr-2'):
                for rule in self.rules:
                    is_active = rule['is_active']
                    with ui.row().classes('w-full p-4 glass-card rounded-2xl items-center group transition-colors hover:bg-white/5'):
                        # Status indicator line
                        ui.element('div').classes(f'w-1.5 h-10 rounded-full mr-4 { "bg-emerald-500" if is_active else "bg-slate-700" }')
                        
                        with ui.column().classes('gap-0 flex-1 min-w-0'):
                            ui.label(rule['name']).classes('text-white font-bold text-lg truncate')
                            ui.label(rule['dsl_text']).classes('text-[10px] text-slate-500 font-mono truncate max-w-[500px]')
                        
                        # UI status pill display
                        ui.label('ACTIVE' if is_active else 'STANDBY').classes(f'text-[9px] font-black tracking-widest px-2 py-0.5 rounded { "text-emerald-400 bg-emerald-500/10" if is_active else "text-slate-500 bg-slate-700/30" }')
                        
                        # The actual switch
                        ui.switch(value=is_active, on_change=lambda e, rid=rule['id']: (toggle_rule_active(rid, e.value), self.refresh_all_ui())).props('color=emerald dense')
        d.open()

    def confirm_category_delete(self, cat_id: int, on_success=None):
        with ui.dialog() as d, ui.card().classes('glass p-8 rounded-3xl'):
            ui.label("Permanent Extraction?").classes('text-lg font-bold text-white')
            with ui.row().classes('w-full justify-end gap-3 mt-8'):
                def confirm(): 
                    if delete_category(cat_id): d.close(); self.refresh_all_ui(); self.show_category_master()
                ui.button('EXTRACT', on_click=confirm).props('color=pink-500 unelevated')
        d.open()

    def toggle_creation_mode(self):
        self.rule_creation_mode = "guided" if self.rule_creation_mode == "raw" else "raw"
        self.creation_mode_label.text = "Guided Mode" if self.rule_creation_mode == "guided" else "Raw DSL Mode"
        self.render_form_inputs()

    def change_user(self, user_id: int):
        self.current_user_id = user_id
        self.refresh_all_ui()
        self.reset_form()

    def show_sync_status(self):
        # Read current user from the select widget to avoid race conditions
        from app.ui.db_manager import fetch_banks
        current_user = self.user_select.value if hasattr(self, 'user_select') and self.user_select else self.current_user_id
        current_banks = fetch_banks(current_user)
        
        # Use a dialog instead of menu to avoid caching issues
        with ui.dialog() as sync_dialog, ui.card().classes('glass p-6 rounded-3xl w-80 border border-white/10'):
            ui.label('SYNC STATUS').classes('text-[10px] font-black text-indigo-400 tracking-[0.3em] mb-4')
            if current_banks:
                with ui.column().classes('w-full gap-3'):
                    for bank in current_banks:
                        with ui.row().classes('items-center gap-3 p-3 bg-slate-800/30 rounded-xl'):
                            ui.icon('account_balance', color='indigo-400', size='sm')
                            with ui.column().classes('gap-0 flex-1'):
                                ui.label(bank['number']).classes('text-sm font-bold text-white')
                                ui.label(bank.get('type', 'Standard Account').upper()).classes('text-[9px] text-slate-500')
                            ui.icon('check_circle', color='emerald-400/50', size='sm')
            else:
                ui.label('No accounts connected').classes('p-4 text-xs italic text-slate-500 text-center')
            ui.button('CLOSE', on_click=sync_dialog.close).props('flat color=slate-400').classes('mt-4 self-end')
        sync_dialog.open()

    async def dry_run_simulation(self):
        dsl = self.dsl_input.value if self.dsl_input else ""
        if not dsl:
            ui.notify("No DSL content to test", type="warning")
            return
        
        rule_obj, error = try_parse(dsl)
        if error:
            ui.notify(f"Cannot dry run: {error}", type="negative")
            return

        with ui.dialog() as d, ui.card().classes('glass p-8 rounded-3xl w-[700px] border border-indigo-500/20 max-h-[80vh] overflow-hidden'):
            with ui.row().classes('w-full items-center justify-between mb-4'):
                ui.label('DRY RUN TERMINAL').classes('text-[10px] font-black text-indigo-400 tracking-[0.4em]')
                ui.button(icon='close', on_click=d.close).props('flat round dense color=slate-400')
            
            samples = fetch_sample_transactions(self.current_user_id, 50)
            evaluator = RuleEvaluator()
            matches = [tx for tx in samples if evaluator.evaluate_rule(rule_obj, tx)]
            
            if matches:
                ui.label(f"Found {len(matches)} matches in last 50 transactions").classes('text-xs text-emerald-400 mb-4 font-bold')
                with ui.column().classes('w-full gap-2 overflow-y-auto pr-2'):
                    for m in matches:
                        with ui.row().classes('w-full p-4 bg-indigo-500/5 border border-indigo-500/10 rounded-2xl items-center hover:bg-indigo-500/10 transition-colors'):
                            with ui.column().classes('gap-0 flex-1'):
                                ui.label(m['description']).classes('text-sm text-white font-bold truncate')
                                ui.label(f"{m['entity_name'] or 'Unknown Entity'} • {m['transaction_date']}").classes('text-[10px] text-slate-500')
                            ui.label(f"₹{abs(m['amount']):,.2f}").classes('text-indigo-400 font-black font-mono')
            else:
                with ui.column().classes('w-full items-center justify-center py-12 gap-4'):
                    ui.icon('search_off', size='4rem', color='slate-600')
                    ui.label('NO MATCHES FOUND').classes('text-slate-500 font-black tracking-widest text-xs')
                    ui.label('Try adjusting your filters or "where" clauses.').classes('text-slate-600 text-[10px]')
            
            ui.button('CLOSE', on_click=d.close).props('flat color=slate-400').classes('mt-8 self-end')
        d.open()

    def render_lookups(self):
        with ui.dialog() as d, ui.card().classes('glass p-8 rounded-3xl w-[600px] border border-white/10'):
            ui.label('REFERENCE TABLES').classes('text-[10px] font-black text-indigo-400 tracking-[0.4em] mb-4')
            with ui.tabs().classes('w-full') as tabs:
                t1, t2, t3, t4, t5 = ui.tab('Categories'), ui.tab('Tags'), ui.tab('Types'), ui.tab('Payments'), ui.tab('Goals')

            with ui.tab_panels(tabs, value=t1).classes('w-full bg-transparent'):
                with ui.tab_panel(t1):
                    if self.categories:
                        with ui.row().classes('gap-2 flex-wrap'):
                            for c in self.categories:
                                ui.chip(f"{c['id']}: {c['name']} ({c.get('type','')})", color=c.get('color','grey')).props('dense dark')
                    else: ui.label("No categories found").classes('text-gray-500 italic')

                with ui.tab_panel(t2):
                    if self.tags:
                        with ui.row().classes('gap-2 flex-wrap'):
                            for t in self.tags:
                                ui.chip(f"{t['id']}: {t['name']}", color=t.get('color','grey')).props('dense dark')
                    else: ui.label("No tags found").classes('text-gray-500 italic')

                with ui.tab_panel(t3):
                    if self.transaction_types:
                        with ui.row().classes('gap-2 flex-wrap'):
                            for t in self.transaction_types:
                                ui.chip(f"{t['id']}: {t['name']}", color=t.get('color','grey')).props('dense dark')
                    else: ui.label("No types found").classes('text-gray-500 italic')

                with ui.tab_panel(t4):
                    if self.payment_methods:
                        with ui.row().classes('gap-2 flex-wrap'):
                            for p in self.payment_methods:
                                ui.chip(f"{p['id']}: {p['type']}-{p['name']}", color=p.get('color','grey')).props('dense dark')
                    else: ui.label("No payment methods found").classes('text-gray-500 italic')

                with ui.tab_panel(t5):
                    if self.goals:
                        with ui.row().classes('gap-2 flex-wrap'):
                            for g in self.goals:
                                ui.chip(f"{g['id']}: {g['name']}", color=g.get('color','grey')).props('dense dark')
                    else: ui.label("No active goals found").classes('text-gray-500 italic')
            ui.button('CLOSE', on_click=d.close).props('flat color=slate-400').classes('mt-8 self-end')
        d.open()

    def build_ui(self):
        apply_styles()
        self._render_header()
        self._render_main_layout()

    def _render_header(self):
        with ui.header().classes('bg-transparent p-4 items-center justify-center'):
            with ui.row().classes('w-full max-w-none px-8 py-3 glass rounded-2xl items-center gap-6 shadow-2xl'):
                with ui.row().classes('items-center gap-4'):
                    with ui.element('div').classes('p-2 bg-gradient-to-tr from-indigo-500 to-purple-600 rounded-xl shadow-lg shadow-indigo-500/20'):
                        ui.icon('apps', color='white', size='1.5rem')
                    ui.label('EXPENSEBOARD').classes('text-2xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400')
                
                ui.space()
                
                with ui.row().classes('items-center gap-4'):
                    with ui.row().classes('items-center gap-2 px-3 py-1 bg-green-500/10 border border-green-500/20 rounded-full'):
                        ui.element('div').classes('w-2 h-2 rounded-full bg-green-400 animate-pulse')
                        ui.label('LIVE').classes('text-[10px] font-bold text-green-400 tracking-widest')
                        ui.button(on_click=self.show_sync_status).props('flat dense icon=expand_more color=green-400').classes('ml-1 scale-75')
                    
                    user_options = {u['id']: u['name'] for u in self.users}
                    self.user_select = ui.select(
                        options=user_options,
                        value=self.current_user_id if self.current_user_id in user_options else None,
                        on_change=lambda e: self.change_user(e.value)
                    ).props('dark dense borderless hide-dropdown-icon').classes('text-slate-300 font-semibold hover:text-white transition-colors')
                    
                    ui.button(icon='refresh', on_click=lambda: (self.refresh_all_ui(), ui.notify('Refreshed'))).props('flat round color=slate-400').classes('hover:rotate-180 transition-transform duration-500')

    def _render_main_layout(self):
        with ui.column().classes('w-full p-8 gap-8'):
            self.dashboard_container = ui.column().classes('w-full')
            with self.dashboard_container: self.render_dashboard()
            
            with ui.row().classes('w-full gap-8 items-start'):
                # Property Panel (Rule Editor)
                self._render_property_panel()
                
                # Rule List Panel
                self._render_rules_list_panel()
            
            # Transaction Ledger Section
            self.render_ledger_section()

    def _render_property_panel(self):
        with ui.card().classes('w-[420px] glass-card p-6 rounded-3xl property-panel'):
            self.form_title = ui.label("PROPERTIES").classes('text-[10px] font-black text-indigo-400 tracking-[0.4em]')
            ui.button(icon='tune', on_click=self.toggle_creation_mode).props('flat round').classes('absolute top-4 right-4')
            self.creation_mode_label = ui.label('Raw DSL Mode').classes('text-[9px] font-bold text-slate-600 uppercase mb-4')
            self.name_input = ui.input(label='Rule Name').classes('w-full').props('outlined dark color=indigo')
            self.priority_input = ui.number(label='Priority Rank', value=100).classes('w-full').props('outlined dark color=indigo')
            self.render_targeting_panel()
            self.dsl_input_container = ui.column().classes('w-full mt-4')
            with self.dsl_input_container: self.render_form_inputs()
            with ui.row().classes('w-full justify-between mt-8'):
                ui.button('DRY RUN', icon='play_arrow', on_click=self.dry_run_simulation).props('flat color=indigo-300')
                ui.button('SAVE RULE', on_click=self.save_rule_handler).props('color=indigo-500 unelevated').classes('rounded-xl font-bold px-8')

    def _render_rules_list_panel(self):
        with ui.column().classes('flex-1 min-w-[600px] gap-4'):
            with ui.row().classes('w-full items-center justify-between px-2'):
                    with ui.row().classes('items-center gap-4'):
                        ui.input(placeholder='Search rules...', on_change=lambda e: (setattr(self, 'search_text', e.value), self.refresh_rules_list())).classes('w-64 glass rounded-xl px-4 py-1')
                        ui.button('REFERENCE IDS', icon='table_chart', on_click=self.render_lookups).props('flat color=indigo-300').classes('text-[10px] font-black tracking-widest')
                    ui.button('PURGE', icon='delete_sweep', on_click=self.delete_selected).props('flat color=pink-400')
            self.rules_container = ui.column().classes('w-full')
            with self.rules_container: self.render_rules_list()

    def render_ledger_section(self):
        """Builds the static header and filtering controls for the ledger."""
        self.ledger_container = ui.column().classes('w-full mt-12')
        with self.ledger_container:
            with ui.row().classes('w-full items-center justify-between mb-4'):
                with ui.row().classes('items-center gap-4'):
                    ui.label('TRANSACTION LEDGER').classes('text-[10px] font-black text-indigo-400 tracking-[0.4em]')
                    ui.input(placeholder='Search entity/desc...', on_change=lambda e: (setattr(self, 'txn_search_text', e.value), self.refresh_transactions_table())).classes('w-64 glass rounded-xl px-4 py-1')
                    
                    with ui.row().classes('items-center gap-1 bg-white/5 px-2 py-1 rounded-xl border border-white/10'):
                        ui.icon('event', color='slate-400', size='xs')
                        from_in = ui.input(placeholder='From', value=self.txn_date_from, on_change=lambda e: (setattr(self, 'txn_date_from', e.value), self.refresh_transactions_table())).props('dense borderless dark').classes('w-20 text-[10px] font-mono')
                        with from_in:
                            with ui.menu().props('no-parent-event') as m1: ui.date().bind_value(from_in)
                            ui.button(icon='arrow_drop_down', on_click=m1.open).props('flat dense').classes('cursor-pointer')
                        
                        ui.label('-').classes('text-slate-600')
                        
                        to_in = ui.input(placeholder='To', value=self.txn_date_to, on_change=lambda e: (setattr(self, 'txn_date_to', e.value), self.refresh_transactions_table())).props('dense borderless dark').classes('w-20 text-[10px] font-mono')
                        with to_in:
                            with ui.menu().props('no-parent-event') as m2: ui.date().bind_value(to_in)
                            ui.button(icon='arrow_drop_down', on_click=m2.open).props('flat dense').classes('cursor-pointer')

                    ui.switch('Uncategorized Only', value=self.txn_uncategorized_only, on_change=lambda e: (setattr(self, 'txn_uncategorized_only', e.value), self.refresh_transactions_table())).props('dense color=indigo dark').classes('text-[10px] font-bold text-slate-400 uppercase tracking-widest')
                
                with ui.row().classes('items-center gap-2'):
                    ui.button('APPLY ALL RULES', on_click=self.handle_run_engine, icon='auto_fix_high').props('outline color=indigo-400 size=sm').classes('px-4 rounded-xl font-bold')
                    with ui.element('q-btn-dropdown').props('flat round dense dropdown-icon=more_vert no-icon-animation color=slate-400'):
                        with ui.list().props('dark'):
                            with ui.item(on_click=lambda: self.show_bulk_update('category_id')).props('clickable v-close-popup'):
                                with ui.item_section(): ui.label('Bulk Set Category').classes('text-xs')
                            with ui.item(on_click=lambda: self.show_bulk_update('tag_id')).props('clickable v-close-popup'):
                                with ui.item_section(): ui.label('Bulk Set Tag').classes('text-xs')
            
            self.ledger_body = ui.column().classes('w-full')
            with self.ledger_body:
                self.refresh_transactions_table()

    def refresh_transactions_table(self):
        """Updates only the table content based on current filters."""
        self.ledger_body.clear()
        
        # Filtering logic
        filtered_txns = self.transactions
        if self.txn_search_text:
            s = self.txn_search_text.lower()
            filtered_txns = [t for t in filtered_txns if s in (t['entity_name'] or '').lower() or s in (t['description'] or '').lower()]
        if self.txn_uncategorized_only:
            filtered_txns = [t for t in filtered_txns if not t['category_id']]
        
        if self.txn_date_from:
            filtered_txns = [t for t in filtered_txns if str(t['transaction_date']) >= self.txn_date_from]
        if self.txn_date_to:
            filtered_txns = [t for t in filtered_txns if str(t['transaction_date']) <= self.txn_date_to]

        with self.ledger_body:
            columns = [
                {'name': 'id', 'label': 'ID', 'field': 'id', 'required': True, 'align': 'left'},
                {'name': 'transaction_date', 'label': 'DATE', 'field': 'transaction_date', 'sortable': True, 'align': 'left'},
                {'name': 'entity_name', 'label': 'ENTITY', 'field': 'entity_name', 'sortable': True, 'align': 'left'},
                {'name': 'amount', 'label': 'AMOUNT', 'field': 'amount', 'sortable': True, 'align': 'right'},
                {'name': 'category_id', 'label': 'CATEGORY', 'field': 'category_id', 'align': 'left'},
                {'name': 'tag_id', 'label': 'TAG', 'field': 'tag_id', 'align': 'left'},
                {'name': 'goal_id', 'label': 'GOAL', 'field': 'goal_id', 'align': 'left'},
                {'name': 'payment_method', 'label': 'METHOD', 'field': 'payment_method_name', 'align': 'left'},
                {'name': 'applied_rule', 'label': 'RULE', 'field': 'applied_rule_name', 'align': 'left'},
            ]
            
            self.txns_table = ui.table(columns=columns, rows=filtered_txns, row_key='id', selection='multiple', pagination={'rowsPerPage': 10}).classes('w-full glass-card border border-white/5')
            with self.txns_table as table:
                # Date format
                table.add_slot('body-cell-transaction_date', r'''
                    <q-td :props="props">
                        <div class="text-[10px] text-slate-400 font-mono">{{ new Date(props.value).toLocaleDateString() }}</div>
                    </q-td>
                ''')
                
                # Amount highlighting
                table.add_slot('body-cell-amount', r'''
                    <q-td :props="props">
                        <div class="font-mono font-bold" :class="props.value > 0 ? 'text-emerald-400' : 'text-rose-400'">
                            ₹{{ Math.abs(props.value).toLocaleString('en-IN', {minimumFractionDigits: 2}) }}
                        </div>
                    </q-td>
                ''')

                # Applied Rule display
                table.add_slot('body-cell-applied_rule', r'''
                    <q-td :props="props">
                        <div v-if="props.value" class="text-[9px] text-indigo-400/80 font-mono truncate max-w-[100px]" :title="props.value">
                            {{ props.value }}
                        </div>
                        <div v-else class="text-[9px] text-slate-700 italic">Manual</div>
                    </q-td>
                ''')

                # Category Dropdown
                table.add_slot('body-cell-category_id', r'''
                    <q-td :props="props">
                        <q-select
                            dense
                            borderless
                            v-model="props.row.category_id"
                            :options="props.cols.find(c => c.name === 'category_id').options"
                            map-options
                            emit-value
                            option-value="id"
                            option-label="name"
                            dark
                            @update:model-value="val => $parent.$emit('update_cell', props.row.id, 'category_id', val)"
                            class="text-xs"
                        >
                            <template v-slot:selected-item="scope">
                                <q-badge v-if="scope.opt" :style="{backgroundColor: scope.opt.color || '#475569'}" class="text-[9px] px-2 py-0.5 shadow-sm">
                                    {{ scope.opt.name }}
                                </q-badge>
                            </template>
                        </q-select>
                    </q-td>
                ''')
                
                # Tag Dropdown
                table.add_slot('body-cell-tag_id', r'''
                    <q-td :props="props">
                        <q-select
                            dense
                            borderless
                            v-model="props.row.tag_id"
                            :options="props.cols.find(c => c.name === 'tag_id').options"
                            map-options
                            emit-value
                            option-value="id"
                            option-label="name"
                            dark
                            @update:model-value="val => $parent.$emit('update_cell', props.row.id, 'tag_id', val)"
                            class="text-xs"
                        >
                            <template v-slot:selected-item="scope">
                                <q-badge v-if="scope.opt" :style="{backgroundColor: scope.opt.color || '#64748b'}" class="text-[9px] px-2 py-0.5">
                                    {{ scope.opt.name }}
                                </q-badge>
                                <span v-else class="text-slate-600 italic">None</span>
                            </template>
                        </q-select>
                    </q-td>
                ''')

                # Goal Dropdown
                table.add_slot('body-cell-goal_id', r'''
                    <q-td :props="props">
                        <q-select
                            dense
                            borderless
                            v-model="props.row.goal_id"
                            :options="props.cols.find(c => c.name === 'goal_id').options"
                            map-options
                            emit-value
                            option-value="id"
                            option-label="name"
                            dark
                            @update:model-value="val => $parent.$emit('update_cell', props.row.id, 'goal_id', val)"
                            class="text-xs"
                        >
                            <template v-slot:selected-item="scope">
                                <span v-if="scope.opt && scope.opt.id" class="text-indigo-300 font-bold tracking-tighter">{{ scope.opt.name }}</span>
                                <span v-else class="text-slate-600 italic">None</span>
                            </template>
                        </q-select>
                    </q-td>
                ''')

                # Pass options to columns for JS access
                table.columns[4]['options'] = [{'id': None, 'name': 'None', 'color': '#1e293b'}] + self.categories
                table.columns[5]['options'] = [{'id': None, 'name': 'None', 'color': '#1e293b'}] + self.tags
                table.columns[6]['options'] = [{'id': None, 'name': 'None', 'color': '#1e293b'}] + self.goals
                
                table.on('update_cell', lambda msg: self.handle_cell_update(msg.args[0], msg.args[1], msg.args[2]))

    def handle_cell_update(self, txn_id: int, field: str, value: Any):
        if update_transaction_field(txn_id, field, value):
            ui.notify(f"Transaction updated", type='positive', color='emerald-500')
            self.load_data() # Reload data to get updated joins/etc
            self.refresh_transactions_table()
        else:
            ui.notify("Update failed", type='negative')

    async def handle_run_engine(self):
        from nicegui import run
        
        # Use a dialog with spinner for better UX
        with ui.dialog() as progress_dialog, ui.card().classes('glass p-8 rounded-3xl items-center gap-4'):
            ui.spinner(size='lg', color='indigo')
            ui.label('Running rule engine...').classes('text-white font-bold')
        
        progress_dialog.open()
        
        try:
            # Run the heavy processing in a separate thread to keep UI responsive
            count = await run.cpu_bound(process_transactions_with_rules, self.current_user_id, self.rules)
            
            progress_dialog.close()
            if count > 0:
                ui.notify(f"SUCCESS: Processed {count} transactions!", type='positive', color='emerald-500', icon='done_all', timeout=4)
                self.refresh_all_ui()
            else:
                ui.notify("No matches found for active rules.", type='info', icon='info', timeout=4)
        except Exception as e:
            progress_dialog.close()
            ui.notify(f"Engine Error: {str(e)}", type='negative', icon='error')

    def show_bulk_update(self, field: str):
        if not self.txns_table.selected:
            ui.notify("No transactions selected", type="warning")
            return
        
        ids = [row['id'] for row in self.txns_table.selected]
        options = []
        if field == 'category_id': options = self.categories
        elif field == 'tag_id': options = self.tags
        
        with ui.dialog() as d, ui.card().classes('glass p-8 rounded-3xl w-96 border border-white/10'):
            ui.label(f'Bulk Set {field.split("_")[0].capitalize()}').classes('text-xl font-bold text-white mb-4')
            ui.label(f'Will update {len(ids)} transactions').classes('text-xs text-slate-500 mb-6')
            
            sel = ui.select(options={o['id']: o['name'] for o in options}, label='Select Value').classes('w-full').props('outlined dark')
            
            with ui.row().classes('w-full justify-end mt-8 gap-4'):
                ui.button('CANCEL', on_click=d.close).props('flat color=slate-400')
                ui.button('APPLY', on_click=lambda: self.handle_bulk_update(ids, field, sel.value, d)).props('color=indigo-500 unelevated')
        d.open()

    def handle_bulk_update(self, ids: List[int], field: str, value: Any, dialog):
        count = update_transactions_bulk(ids, field, value)
        if count > 0:
            ui.notify(f"Bulk updated {count} transactions", type='positive')
            dialog.close()
            self.refresh_all_ui()
        else:
            ui.notify("Update failed", type='negative')

    def set_filter(self, key, val):
        if key == 'active': self.active_filter = val; self.category_filter = None
        elif key == 'category': self.category_filter = val; self.active_filter = None
        else: self.active_filter = None; self.category_filter = None
        self.refresh_rules_list()

    async def delete_selected(self):
        selected = getattr(self, 'rules_table', None)
        if not (selected and selected.selected): return
        for row in selected.selected: delete_rule(row['id'])
        self.refresh_all_ui()
