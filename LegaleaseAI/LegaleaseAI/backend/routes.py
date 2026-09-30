from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class DocumentRequest(BaseModel):
    document_type: str
    parties: str
    terms: str
    effective_date: str


@router.post("/generate")
def generate_document(request: DocumentRequest):

    text = f"""
LEGAL DOCUMENT

Document Type:
{request.document_type}

Parties:
{request.parties}

Effective Date:
{request.effective_date}

Terms & Conditions:
{request.terms}
"""

    return {
        "success": True,
        "document": text.strip()
    }