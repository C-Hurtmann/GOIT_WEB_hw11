from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import ContactModel, ContactResponce
from src.repository import contacts as repo_contacts


router = APIRouter(prefix='/contacts', tags=['contacts'])

@router.get('/', response_model=List[ContactResponce])
async def read_contacts(skip: int, limit: int, db: Session = Depends(get_db)):
    result = await repo_contacts.get_contacts(skip, limit, db)
    return result

@router.get('/{contact_id}', response_model=ContactResponce)
async def read_contact(contact_id: int, db: Session = Depends(get_db)):
    result = await repo_contacts.get_contact(contact_id, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return result

@router.post('/', response_model=ContactResponce)
async def create_contact(body: ContactModel, db: Session = Depends(get_db)):
    return await repo_contacts.create_contact(body, db)