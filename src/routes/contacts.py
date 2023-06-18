from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import ContactModel, ContactResponce
from src.repository import contacts as repo_contacts


router = APIRouter(prefix='/contacts', tags=['contacts'])

@router.get('/', response_model=List[ContactResponce])
async def get_contacts(skip: int,
                        limit: int,
                        db: Session = Depends(get_db),
                        first_name: str = Query(None, description='filter by first name'),
                        last_name: str = Query(None, description='filter by last name'),
                        email: str = Query(None, description='filter by email')):
    result = await repo_contacts.get_contacts(skip, limit, db, first_name, last_name, email)
    return result

@router.get('/bithday_on_next_week', response_model=List[ContactResponce])
async def get_contacts_with_birthday_on_next_week(db: Session = Depends(get_db)):
    result = await repo_contacts.get_contacts_with_bithday_on_next_week(db)    
    return result

@router.get('/{contact_id}', response_model=ContactResponce)
async def get_contact(contact_id: int, db: Session = Depends(get_db)):
    result = await repo_contacts.get_contact(contact_id, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return result

@router.post('/', response_model=ContactResponce)
async def create_contact(body: ContactModel, db: Session = Depends(get_db)):
    return await repo_contacts.create_contact(body, db)

@router.put('/{contact_id}')
async def update_contact(contact_id: int, body: ContactModel, db: Session = Depends(get_db)):
    result = await repo_contacts.update_contact(contact_id, body, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return result

@router.delete('/{contact_id}')
async def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    result = await repo_contacts.delete_contact(contact_id, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return result