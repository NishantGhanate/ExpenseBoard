"""
Api for documents pwd
"""
import logging
from datetime import date
from typing import List, Optional

from app.api.v1 import PREFIX
from app.core.database import get_cursor
from app.tasks.rule_engine_task import run_rule_engine
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(name="app")

rule_engine_router = APIRouter(prefix=PREFIX)


# Define a schema for the incoming request
class RuleEnginePayload(BaseModel):
    """
    Docstring for FileCredentialsRequest
    """
    user_email: EmailStr
    bank_account_id: Optional[int] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    rules_id: Optional[List[int]] = []



@rule_engine_router.post("/rule-engine", status_code=status.HTTP_200_OK)
async def rule_engine(request_data: RuleEnginePayload

):
    """
    - Given payload runs rule-engine on specified params
    """

    try:
        # 1. Get a cursor from the pool
        with get_cursor() as cur:

            request_params = request_data.model_dump()

            # 3. Call the function passing the cursor
            result = run_rule_engine(**request_params, cur=cur)

            return result

    except Exception as e:
        logger.exception("Upload failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e

