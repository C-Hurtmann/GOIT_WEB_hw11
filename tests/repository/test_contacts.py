import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.repository import contacts as repo_contacts


class TestContacts(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.contacts = [Contact(first_name='Bob'), Contact(first_name='Bill'), Contact(first_name='Bruce')]
        self.session.query().filter().offset().limit().all.return_value = self.contacts
    
    async def test_get_contacts_without_filters(self):
        result = await repo_contacts.get_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, self.contacts)
    
    async def test_get_contacts_with_one_filter(self):
        result = await repo_contacts.get_contacts(skip=0, limit=10, user=self.user, db=self.session, first_name='Bob')
        self.assertListEqual(result, self.contacts[:1])


if __name__ == '__main__':
    unittest.main()