from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
#from ..dependencies import get_current_user
from ..models import Payload
from app.service import external as external_service
from ..schemas import PayloadCreate, PayloadOut

router = APIRouter(prefix="/payloads", tags=["payloads"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=None)
def _create_(
    #list1: List[str] = Query(..., description="List 1 of strings to be processed"),
    #list2: List[str] = Query(..., description="List 2 of strings to be processed")
    payload_data: PayloadCreate,
    db: Annotated[Session, Depends(get_db)]
) -> int:
    #external_service.transform_payload(list1, list2)
    payload = Payload(text=external_service.transform_payload(payload_data.list1, payload_data.list2))
    print (f"Создан payload: {external_service.transform_payload(payload_data.list1, payload_data.list2)}")
    db.add(payload)
    db.commit()
    db.refresh(payload)
    
    return payload.id

@router.get("/", response_model=PayloadOut)
def get_payload(
    db: Annotated[Session, Depends(get_db)]
) -> Payload:
    payload = db.execute(select(Payload).order_by(Payload.id.desc())).scalars().first()

    if payload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="payload not found")

    return payload
