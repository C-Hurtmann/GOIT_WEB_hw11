from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(50))
    phone = Column(String(20))
    birthday = Column(Date)
