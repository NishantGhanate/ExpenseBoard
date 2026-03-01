import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import psycopg
from app.rule_engine.evaluator import RuleEvaluator
from app.rule_engine.parser import try_parse
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()

@dataclass
class Rule:
    id: Optional[int]
    name: str
    dsl_text: str
    priority: int
    user_id: int
    is_active: bool = True

def get_db_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        user = os.getenv("DATABASE_USER")
        password = os.getenv("DATABASE_PASSWORD")
        host = os.getenv("DATABASE_HOST")
        port = os.getenv("DATABASE_PORT", "5432")
        db_name = os.getenv("DATABASE_NAME")

        if all([user, password, host, db_name]):
            url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
        else:
            raise ValueError("DATABASE_URL is missing, and individual variables are also incomplete.")
    return url

def get_connection():
    try:
        return psycopg.connect(get_db_url(), row_factory=dict_row)
    except Exception as e:
        print(f"Connection Error: {e}")
        raise

import functools


def safe_db_call(default_return=None):
    """Decorator to wrap DB calls with try-except block."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"DB Error in {func.__name__}: {e}")
                return default_return
        return wrapper
    return decorator

@safe_db_call(default_return=[])
def fetch_rules(user_id: int = 1) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, dsl_text, priority, user_id, is_active, created_at, updated_at
                FROM ss_categorization_rules WHERE user_id = %s ORDER BY priority ASC, name ASC
            """, (user_id,))
            return cur.fetchall()

@safe_db_call(default_return=None)
def fetch_rule_by_id(rule_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, dsl_text, priority, user_id, is_active FROM ss_categorization_rules WHERE id = %s", (rule_id,))
            return cur.fetchone()

@safe_db_call(default_return=None)
def save_rule(rule: Rule) -> Optional[int]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            if rule.id:
                cur.execute("UPDATE ss_categorization_rules SET name = %s, dsl_text = %s, priority = %s, is_active = %s WHERE id = %s RETURNING id",
                           (rule.name, rule.dsl_text, rule.priority, rule.is_active, rule.id))
            else:
                cur.execute("INSERT INTO ss_categorization_rules (name, dsl_text, priority, user_id, is_active) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                           (rule.name, rule.dsl_text, rule.priority, rule.user_id, rule.is_active))
            conn.commit()
            res = cur.fetchone()
            return res['id'] if res else None

@safe_db_call(default_return=False)
def delete_rule(rule_id: int) -> bool:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM ss_categorization_rules WHERE id = %s", (rule_id,))
            conn.commit()
            return cur.rowcount > 0

@safe_db_call(default_return=False)
def toggle_rule_active(rule_id: int, is_active: bool) -> bool:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE ss_categorization_rules SET is_active = %s WHERE id = %s", (is_active, rule_id))
            conn.commit()
            return cur.rowcount > 0

@safe_db_call(default_return=[])
def fetch_sample_transactions(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.id, t.entity_name, t.description, t.amount, tt.name as type, t.transaction_date
                FROM ss_transactions t
                JOIN ss_transaction_types tt ON t.type_id = tt.id
                WHERE t.user_id = %s AND t.category_id IS NULL
                ORDER BY t.transaction_date DESC
                LIMIT %s
            """, (user_id, limit))
            return cur.fetchall()

@safe_db_call(default_return=[])
def fetch_lookup(query: str) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

def fetch_categories(): return fetch_lookup("SELECT id, name, type, color FROM ss_categories WHERE is_active = TRUE ORDER BY name")
def fetch_tags(): return fetch_lookup("SELECT id, name, color FROM ss_tags WHERE is_active = TRUE ORDER BY name")
def fetch_payment_methods(): return fetch_lookup("SELECT id, type, name, color FROM ss_payment_methods WHERE is_active = TRUE ORDER BY type, name")
def fetch_transaction_types(): return fetch_lookup("SELECT id, name, color FROM ss_transaction_types WHERE is_active = TRUE ORDER BY name")
def fetch_goals(): return fetch_lookup("SELECT id, name, target_amount, status, color FROM ss_goals WHERE status = 'ACTIVE' ORDER BY name")

@safe_db_call(default_return=[])
def fetch_banks(user_id: int = 1) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, user_id, number, ifsc_code, type, is_active
                FROM ss_bank_accounts WHERE user_id = %s AND is_active = TRUE
            """, (user_id,))
            return cur.fetchall()

@safe_db_call(default_return=[{'id': 1, 'name': 'Default', 'email': ''}])
def fetch_users():
    users = fetch_lookup("SELECT id, name, email FROM ss_users WHERE is_active = TRUE ORDER BY name")
    return users if users else [{'id': 1, 'name': 'Default', 'email': ''}]

@safe_db_call(default_return=False)
def save_category(cat: dict) -> bool:
    with get_connection() as conn:
        with conn.cursor() as cur:
            if cat.get('id'):
                cur.execute("""
                    UPDATE ss_categories
                    SET name = %s, type = %s, color = %s
                    WHERE id = %s
                """, (cat['name'], cat.get('type'), cat.get('color'), cat['id']))
            else:
                cur.execute("""
                    INSERT INTO ss_categories (name, type, color)
                    VALUES (%s, %s, %s)
                """, (cat['name'], cat.get('type'), cat.get('color')))
            conn.commit()
            return cur.rowcount > 0

@safe_db_call(default_return=False)
def delete_category(cat_id: int) -> bool:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM ss_categories WHERE id = %s", (cat_id,))
            conn.commit()
            return cur.rowcount > 0

@safe_db_call(default_return=[])
def fetch_transactions(user_id: int = 1, limit: int = 1000) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Ensure applied_rule_id column exists (simple migration check)
            try:
                cur.execute("ALTER TABLE ss_transactions ADD COLUMN IF NOT EXISTS applied_rule_id INTEGER REFERENCES ss_categorization_rules(id) ON DELETE SET NULL;")
                conn.commit()
            except Exception:
                conn.rollback()

            cur.execute("""
                SELECT
                    t.id, t.transaction_date, t.entity_name, t.amount, t.currency, t.description,
                    t.bank_account_number, t.type_name, t.category_name, t.category_id,
                    t.tag_name, t.tag_id, t.goal_name, t.goal_id, t.payment_method_name,
                    r.name as applied_rule_name
                FROM ss_v_transactions t
                JOIN ss_transactions st ON st.id = t.id
                LEFT JOIN ss_categorization_rules r ON r.id = st.applied_rule_id
                WHERE t.user_id = %s
                ORDER BY t.transaction_date DESC
                LIMIT %s
            """, (user_id, limit))
            return cur.fetchall()

@safe_db_call(default_return=0)
def process_transactions_with_rules(user_id: int, rules_list: List[Dict[str, Any]]) -> int:


    # Fetch uncategorized transactions
    txns = fetch_sample_transactions(user_id, 500)

    evaluator = RuleEvaluator()
    parsed_rules = []
    for r in rules_list:
        if r['is_active']:
            rule_obj, _ = try_parse(r['dsl_text'])
            if rule_obj:
                parsed_rules.append((r['id'], rule_obj))

    updated_count = 0
    with get_connection() as conn:
        with conn.cursor() as cur:
            for tx in txns:
                for rule_id, rule_obj in parsed_rules:
                    if evaluator.evaluate_rule(rule_obj, tx):
                        # Apply assignments
                        assignments = rule_obj.assignment.fields
                        if not assignments: continue

                        set_clauses = []
                        params = []
                        for field, val in assignments.items():
                            set_clauses.append(f"{field} = %s")
                            params.append(val)

                        set_clauses.append("applied_rule_id = %s")
                        params.append(rule_id)
                        params.append(tx['id'])

                        query = f"UPDATE ss_transactions SET {', '.join(set_clauses)} WHERE id = %s"
                        cur.execute(query, tuple(params))
                        updated_count += 1
                        break # First matching rule wins
            conn.commit()
    return updated_count

@safe_db_call(default_return=False)
def update_transaction_field(txn_id: int, field: str, value: Any) -> bool:
    allowed_fields = {'category_id', 'tag_id', 'goal_id', 'type_id', 'payment_method_id'}
    if field not in allowed_fields:
        return False
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"UPDATE ss_transactions SET {field} = %s, updated_at = NOW() WHERE id = %s", (value, txn_id))
            conn.commit()
            return cur.rowcount > 0

@safe_db_call(default_return=0)
def update_transactions_bulk(txn_ids: List[int], field: str, value: Any) -> int:
    allowed_fields = {'category_id', 'tag_id', 'goal_id', 'type_id', 'payment_method_id'}
    if field not in allowed_fields:
        return 0
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"UPDATE ss_transactions SET {field} = %s, updated_at = NOW() WHERE id = ANY(%s)", (value, list(txn_ids)))
            conn.commit()
            return cur.rowcount
