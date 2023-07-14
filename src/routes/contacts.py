from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactModel, ContactResponce
from src.repository import contacts as repo_contacts
from src.services.auth import auth_service


router = APIRouter(prefix='/contacts', tags=['contacts'])

@router.get('/', response_model=List[ContactResponce],)
            #dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contacts(skip: int,
                        limit: int,
                        current_user: User = Depends(auth_service.get_current_user),
                        db: Session = Depends(get_db),
                        first_name: str = Query(None, description='filter by first name'),
                        last_name: str = Query(None, description='filter by last name'),
                        email: str = Query(None, description='filter by email')):
    """
    Retrieve all contacts created by current user. Login required.
    
    :param skip: Skip first n rows.
    :type skip: int
    :param limit: Limit retrieve by n rows
    :type limit: int
    :param current_user: Logined user.
    :type current_user: User
    :param db: Database session
    :type db: Session
    :param first_name: Filter by first name.
    :type first_name: str
    :param last_name: Filter by last name.
    :type last_name: str
    :param email: Filter by email.
    :type email: str
    :return: List of contacts.
    :rtype: List[ContactResponce]
    """
    result = await repo_contacts.get_contacts(skip, limit, current_user, db, first_name, last_name, email)
    return result


@router.get('/bithday_on_next_week', response_model=List[ContactResponce],)
            #dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contacts_with_birthday_on_next_week(current_user: User = Depends(auth_service.get_current_user),
                                                  db: Session = Depends(get_db)):
    """
    Retrieve list of contacts with birthday on next week. Login required.
    
    :param current_user: Logined user.
    :type current_user: User
    :param db: Database session.
    :type db: Session
    :return: List of contacts with birthday on next week.
    :rtype: List[ContactResponce]
    """

    result = await repo_contacts.get_contacts_with_bithday_on_next_week(current_user, db)    
    return result


@router.get('/{contact_id}', response_model=ContactResponce,)
            #dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contact(contact_id: int,
                      current_user: User = Depends(auth_service.get_current_user),
                      db: Session = Depends(get_db)):
    """
    Retrieve contact by id. Login required.
    
    If contact is not found, raise 404 error.
    
    :param contact_id: ID of contact.
    :type contact_id: int
    :param current_user: Logined user.
    :type current_user: User
    :param db: Database session.
    :type db: Session
    :return: Contact found by ID.
    :rtype: ContactResponce
    """

    result = await repo_contacts.get_contact(contact_id, current_user, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return result


@router.post('/', response_model=ContactResponce, status_code=status.HTTP_201_CREATED,)
             #dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def create_contact(body: ContactModel,
                         current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    """
    Create new contact. Login required.
    
    Return new contact info with 201 status.
    
    :param body: Info for creating contacts.
    :type body: ContactModel
    :param current_user: Logined user.
    :type current_user: User
    :param db: Database session.
    :type db: Session
    :return: Created user info.
    :rtype: ContactResponce
    """

    return await repo_contacts.create_contact(body, current_user, db)


@router.put('/{contact_id}',)
            #dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def update_contact(contact_id: int,
                         body: ContactModel,
                         current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    """
    Update contact info. Login required.
    
    If contact is not found, raise 404 error. 
    
    :param contact_id: Contact id to update.
    :type contact_id: int
    :param body: Updated contact info.
    :type body: ContactModel
    :param current_user: Logined user.
    :type current_user: User
    :param db: Database session.
    :type db: Session
    :return: Updated user info.
    :rtype: ContactResponce
    """

    result = await repo_contacts.update_contact(contact_id, body, current_user, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return result


@router.delete('/{contact_id}',)
               #dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def delete_contact(contact_id: int,
                         current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    """
    Delete contact. Login required.
    
    If contact is not found, raise 404 error.
    
    :param contact_id: Contact id to delete.
    :type contact_id: int
    :param current_user: Logined user.
    :type current_user: User
    :param db: Database session.
    :type db: Session
    :return: Message.
    :rtype: dict
    """

    result = await repo_contacts.delete_contact(contact_id, current_user, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return result