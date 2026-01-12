"""
Api for documents pwd
"""
import logging

from app.api.v1 import PREFIX
from app.core.database import get_cursor
from app.model_actions.statement_pdf import create_or_update_bank_pdf
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(name="app")

file_pwd_router = APIRouter(prefix=PREFIX)


# Define a schema for the incoming request
class FileCredentialsRequest(BaseModel):
    """
    Docstring for FileCredentialsRequest
    """
    user_id: str
    sender_email: EmailStr
    filename: str
    pdf_password: str



@file_pwd_router.post("/file-credentails", status_code=status.HTTP_201_CREATED)
async def file_upload_pwd(request_data: FileCredentialsRequest

):
    """
    - Receives file credentials
    - Creates or updates the record in the database
    """

    try:
        with get_cursor() as curr:
            _ = create_or_update_bank_pdf(
                user_id=request_data.user_id,
                sender_email=request_data.sender_email,
                filename=request_data.filename,
                pdf_password=request_data.pdf_password,
                cur=curr
            )

        return {
            "status": "success",
            "message": "Credentials updated successfully",
            "filename": request_data.filename
        }

    except Exception as e:
        logger.exception("Upload failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e

