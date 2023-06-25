from typing import List, Optional

from datetime import datetime, timedelta
from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel


# GET
async def get_contacts(skip: int,
                       limit: int,
                       user: User,
                       db: Session,
                       first_name: Optional[str] = None,
                       last_name:Optional[str] = None,
                       email: Optional[str] = None) -> List[Contact]:
    filters = []
    if first_name:
        filters.append(Contact.first_name == first_name)
    if last_name:
        filters.append(Contact.last_name == last_name)
    if email:
        filters.append(Contact.email == email)
    filters.append(Contact.user_id == user.id)
    contacts = db.query(Contact).filter(and_(*filters)).offset(skip).limit(limit).all()
    return contacts

async def get_contacts_with_bithday_on_next_week(user: User, db: Session) -> List[Contact]:
    today = datetime.today().date()
    day_after_one_week = today + timedelta(days=7)
    contacts = db.query(Contact).filter(Contact.user_id == user.id).all()
    filtered_contacts = []
    for contact in contacts:
        birthday_date = contact.birthday.replace(year=today.year)
        print(birthday_date, type(birthday_date))
        if birthday_date > today and birthday_date <= day_after_one_week:
            filtered_contacts.append(contact)
    return filtered_contacts

async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    contact = db.query(Contact).filter(and_(
        Contact.id == contact_id,
        Contact.user_id == user.id
        )).first()

    return contact
# POST
async def create_contact(body: ContactModel, user: User, db: Session) -> Contact:
    contact = Contact(first_name=body.first_name,
                      last_name=body.last_name,
                      email=body.email,
                      phone=body.phone,
                      birthday=body.birthday,
                      user=user)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return  contact
# PUT
async def update_contact(contact_id: int, body: ContactModel, user: User, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(and_(
        Contact.id == contact_id,
        Contact.user_id == user.id
        )).first()

    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        db.commit()
        db.refresh(contact)
    return contact
# DELETE
async def delete_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(and_(
        Contact.id == contact_id,
        Contact.user_id == user.id
        )).first()

    if contact:
        db.delete(contact)
        db.commit()
    return contact

