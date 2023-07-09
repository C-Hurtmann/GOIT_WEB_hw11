from pathlib import Path
import sys
import unittest

from benedict import benedict
from sqlalchemy import inspect
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from src.database.models import Contact, User
from src.repository import contacts as repo_contacts
from tests.test_db import TestSession


class TestContactsGet(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.session = TestSession()
        self.user = User(email='example@gmail.com', password='admin')
        
        self.contacts = [Contact(first_name='Bob', last_name='Ross', user=self.user),
                         Contact(first_name='John', last_name='Ross', user=self.user)]

        self.session.add(self.user)
        self.session.commit()
        self.session.add_all(self.contacts)
        self.session.commit()
    
    def tearDown(self):
        self.session.query(User).delete()
        self.session.query(Contact).delete()
        self.session.commit()
# -----------------------------------------------------get_contacts-----------------------------------------------------------------
    async def test_get_contacts_without_filters(self):
        query = await repo_contacts.get_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(query, self.contacts)
    
    async def test_get_contacts_with_one_filter(self):
        query_1 = await repo_contacts.get_contacts(skip=0, limit=10, user=self.user, db=self.session, first_name='Bob')
        self.assertEqual(query_1, self.contacts[:1])
        
        query_2 = await repo_contacts.get_contacts(skip=0, limit=10, user=self.user, db=self.session, last_name='Ross')
        self.assertEqual(query_2, self.contacts)
    
    async def test_get_contacts_with_many_filters(self):
        query = await repo_contacts.get_contacts(skip=0, limit=10, user=self.user, db=self.session, first_name='Bob', last_name='Ross')
        self.assertEqual(query, self.contacts[:1])
        
    async def test_get_contacts_with_offset(self):
        query = await repo_contacts.get_contacts(skip=1, limit=10, user=self.user, db=self.session)
        self.assertEqual(query, self.contacts[1:])        

    async def test_get_contacts_with_limit(self):
        query = await repo_contacts.get_contacts(skip=0, limit=1, user=self.user, db=self.session)
        self.assertEqual(query, self.contacts[:1])
# ------------------------------------------------------get_contact-----------------------------------------------------------------   
    async def test_get_contact_by_id(self):
        contact_id = self.contacts[0].id
        query = await repo_contacts.get_contact(contact_id=contact_id, user=self.user, db=self.session)
        self.assertEqual(query, self.contacts[0])
    
    async def test_get_contact_by_id_not_found(self):
        contact_id = self.contacts[1].id + 1
        query = await repo_contacts.get_contact(contact_id=contact_id, user=self.user, db=self.session)
        self.assertEqual(query, None)


class TestContactsPost(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.session = TestSession()
        self.user = User(email='example@gmail.com', password='admin')   
        self.session.add(self.user)
        self.session.commit()
    
    def tearDown(self):
        self.session.query(User).delete()
        self.session.query(Contact).delete()
        self.session.commit()

    async def test_create_contact(self):
        body = benedict({
            "first_name": "Bob",
            "last_name": "Ross",
            "email": "user@example.com",
            "phone": "+380227100937",
            "birthday": "2023-07-09"
            })
        
        result = await repo_contacts.create_contact(body, self.user, self.session)
        query = self.session.query(Contact).first()
        self.assertEqual(result, query)
        self.assertEqual(result.id, query.id)


class TestContactsOther(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.session = TestSession()
        self.user = User(email='example@gmail.com', password='admin')   
        self.session.add(self.user)
        self.session.commit()
        self.contact = Contact(first_name='Bob', last_name='Ross', user=self.user)
        self.session.add(self.contact)
        self.session.commit()
    
    def tearDown(self):
        self.session.query(User).delete()
        self.session.query(Contact).delete()
        self.session.commit()    
    
    async def test_update_contact(self):
        target_contact = self.contact
        target_contact_email = target_contact.email
        
        body_to_update = benedict({
            "first_name": "Bob",
            "last_name": "Ross",
            "email": "user@example.com",
            "phone": "+380227100937",
            "birthday": "2023-07-09"
            })
        
        result = await repo_contacts.update_contact(target_contact.id, body_to_update, self.user, self.session)
        self.assertIs(result, target_contact)
        self.assertNotEqual(result.email, target_contact_email)
    
    async def test_delete_contacts(self):
        columns = inspect(Contact).columns
        target_obj_in_dict = benedict({c.name: getattr(self.contact, c.name) for c in columns})
        
        result = await repo_contacts.delete_contact(self.contact.id, self.user, self.session)
        
        self.assertEqual(result.id, target_obj_in_dict.id)
        
        query = self.session.query(Contact).first()
        
        self.assertIsNone(query)
    

if __name__ == '__main__':
    unittest.main()