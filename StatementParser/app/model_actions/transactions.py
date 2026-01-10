import logging
from typing import Any

from app.core.database import get_cursor
from app.pdf_normalizer.utils import ss_transactions_template

logger = logging.getLogger(name="app")


def bulk_insert_transactions(
    transactions: list[dict],
    chunk_size: int = 30
) -> dict[str, Any]:
    """
    Bulk insert with chunking and fallback to individual inserts on failure.

    Returns:
        dict with 'inserted', 'failed', 'errors' keys
    """
    if not transactions:
        return {'inserted': 0, 'failed': 0, 'errors': []}

    column_names = list(ss_transactions_template().keys())
    extras = ['type', 'payment_method']
    for ext in extras:
        column_names.remove(ext)

    try:
        columns_sql = ", ".join(column_names)
        values_sql = ", ".join(["%s"] * len(column_names))

        update_cols = [col for col in column_names if col != "id"]
        set_clause = ", ".join(f"{col} = EXCLUDED.{col}" for col in update_cols)

        query = f"""
        INSERT INTO ss_transactions ({columns_sql})
        VALUES ({values_sql})
        ON CONFLICT (id)
        DO UPDATE SET {set_clause}
        """

        total_inserted = 0
        total_failed = 0
        errors = []

        # Process in chunks
        for i in range(0, len(transactions), chunk_size):
            chunk = transactions[i:i + chunk_size]
            values = [tuple(t.get(col) for col in column_names) for t in chunk]

            try:
                with get_cursor() as cur:
                    cur.executemany(query, values)
                    total_inserted += len(chunk)

            except Exception as e:
                logger.warning(f"Chunk {i // chunk_size + 1} failed: {e}. Falling back to individual inserts.")

                # Fallback: insert one by one
                for j, txn in enumerate(chunk):
                    row = tuple(txn.get(col) for col in column_names)
                    try:
                        with get_cursor() as cur:
                            cur.execute(query, row)
                            total_inserted += cur.rowcount

                    except Exception as row_error:
                        total_failed += 1
                        error_info = {
                            'index': i + j,
                            'transaction': txn,
                            'error': str(row_error)
                        }
                        errors.append(error_info)
                        logger.error(f"Failed to insert transaction {i + j}: {row_error}")
                        logger.debug(f"Transaction data: {txn}")

        result = {
            'inserted': total_inserted,
            'failed': total_failed,
            'errors': errors
        }

        if errors:
            logger.warning(f"Bulk insert completed: {total_inserted} inserted, {total_failed} failed")
        else:
            logger.info(f"Bulk insert completed: {total_inserted} inserted")

    except Exception as ex:
        logger.exception("Transactions Bulk insert failure")
        raise ex

    return result
