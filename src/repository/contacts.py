from typing import List

from datetime import datetime, timedelta
from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas import ContactModel

# GET
async def get_contacts(skip: int,
                       limit: int,
                       db: Session,
                       first_name: str = None,
                       last_name: str = None,
                       email: str = None) -> List[Contact]:
    filters = []
    if first_name:
        filters.append(Contact.first_name == first_name)
    if last_name:
        filters.append(Contact.last_name == last_name)
    if email:
        filters.append(Contact.email == email)
    contacts = db.query(Contact).filter(and_(*filters)).offset(skip).limit(limit).all()
    return contacts

async def get_contacts_with_bithday_on_next_week(db: Session) -> List[Contact]:
    today = datetime.today().date()
    day_after_one_week = today + timedelta(days=7)
    contacts = db.query(Contact).all()
    filtered_contacts = []
    for contact in contacts:
        birthday_date = contact.birthday.replace(year=today.year)
        print(birthday_date, type(birthday_date))
        if birthday_date > today and birthday_date <= day_after_one_week:
            filtered_contacts.append(contact)
    return filtered_contacts

async def get_contact(contact_id: int, db: Session) -> Contact:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    return contact
# POST
async def create_contact(body: ContactModel, db: Session) -> Contact:
    contact = Contact(**body.dict())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return  contact
# PUT
async def update_contact(contact_id: int, body: ContactModel, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
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
async def delete_contact(contact_id: int, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact

