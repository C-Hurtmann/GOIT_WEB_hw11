from typing import List

from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas import ContactModel


async def get_contacts(skip: int, limit: int, db: Session) -> List[Contact]:
    result = db.query(Contact).offset(skip).limit(limit).all()
    return result

async def get_contact(contact_id: int, db: Session) -> Contact:
    result = db.query(Contact).filter(Contact.id == contact_id).first()
    return result

async def create_contact(body: ContactModel, db: Session) -> Contact:
    contact = Contact(**body.dict())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return  contact