from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactModel, ContactResponce
from src.repository import contacts as repo_contacts
from src.services.auth import auth_service


router = APIRouter(prefix='/contacts', tags=['contacts'])

@router.get('/', response_model=List[ContactResponce])
async def get_contacts(skip: int,
                        limit: int,
                        current_user: User = Depends(auth_service.get_current_user),
                        db: Session = Depends(get_db),
                        first_name: str = Query(None, description='filter by first name'),
                        last_name: str = Query(None, description='filter by last name'),
                        email: str = Query(None, description='filter by email')):

    result = await repo_contacts.get_contacts(skip, limit, current_user, db, first_name, last_name, email)
    return result

@router.get('/bithday_on_next_week', response_model=List[ContactResponce])
async def get_contacts_with_birthday_on_next_week(current_user: User = Depends(auth_service.get_current_user),
                                                  db: Session = Depends(get_db)):

    result = await repo_contacts.get_contacts_with_bithday_on_next_week(current_user, db)    
    return result

@router.get('/{contact_id}', response_model=ContactResponce)
async def get_contact(contact_id: int,
                      current_user: User = Depends(auth_service.get_current_user),
                      db: Session = Depends(get_db)):

    result = await repo_contacts.get_contact(contact_id, current_user, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return result

@router.post('/', response_model=ContactResponce, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactModel,
                         current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):

    return await repo_contacts.create_contact(body, current_user, db)

@router.put('/{contact_id}')
async def update_contact(contact_id: int,
                         body: ContactModel,
                         current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):

    result = await repo_contacts.update_contact(contact_id, body, current_user, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return result

@router.delete('/{contact_id}')
async def delete_contact(contact_id: int,
                         current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):

    result = await repo_contacts.delete_contact(contact_id, current_user, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return result