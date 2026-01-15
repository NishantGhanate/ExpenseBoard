import logging
from typing import Any

from app.core.database import get_cursor

logger = logging.getLogger(name="app")


def bulk_insert_transactions(
    transactions: list[dict],
    chunk_size: int = 50,
    cur=None,
    update=False
) -> dict[str, Any]:
    """
    Inserts transactions in bulk. If a bulk chunk fails,
    it falls back to row-by-row insertion
    """
    if not transactions:
        return {'inserted': 0, 'failed': 0, 'errors': []}

    # 1. Prepare SQL Components
    column_names = list(transactions[0].keys())

    # DO NOT REMOVE:
    extras = ['type', 'payment_method']
    for ext in extras:
        if ext in column_names:
            column_names.remove(ext)

    columns_sql = ", ".join(column_names)
    values_sql = ", ".join(["%s"] * len(column_names))

    # Update everything except the unique reference and primary key
    update_cols = [c for c in column_names if c not in ['id', 'reference_id', 'created_at', 'updated_at']]
    set_clause = ", ".join(f"{c} = EXCLUDED.{c}" for c in update_cols)

    query = f"""
        INSERT INTO ss_transactions ({columns_sql})
        VALUES ({values_sql})
        ON CONFLICT ON CONSTRAINT uq_transaction_reference
        DO UPDATE SET {set_clause}, updated_at = CURRENT_TIMESTAMP
    """

    result = {'inserted': 0, 'failed': 0, 'errors': []}

    def _process(cursor):
        for i in range(0, len(transactions), chunk_size):
            chunk = transactions[i : i + chunk_size]
            values = [tuple(t.get(col) for col in column_names) for t in chunk]

            try:
                # Try Bulk Insert

                cursor.executemany(query, values)
                result['inserted'] += len(chunk)
            except Exception as bulk_ex:
                logger.warning(f"Bulk chunk {i//chunk_size} failed. Error: {bulk_ex}. Falling back to row-wise.")

                # Fallback: Row-by-row logic
                for j, txn in enumerate(chunk):
                    row_values = tuple(txn.get(col) for col in column_names)
                    try:

                        cursor.execute(query, row_values)
                        result['inserted'] += 1
                    except Exception as row_error:
                        result['failed'] += 1
                        result['errors'].append({
                            'index': i + j,
                            'reference_id': txn.get('reference_id'),
                            'error': str(row_error)
                        })
                        logger.error(f"Failed to insert row {i + j}: {row_error}")

    # 2. Execution logic
    try:
        if cur:
            _process(cur)
        else:
            with get_cursor() as new_cur:
                _process(new_cur)
    except Exception as ex:
        # This only triggers if the connection itself dies, not just a row failure
        logger.exception("Database connection failure during bulk insert")
        raise ex

    return result
