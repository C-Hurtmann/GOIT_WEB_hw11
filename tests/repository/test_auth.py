from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from src.database.models import User
from src.schemas import UserModel
from src.repository import auth as repo_auth
from tests.test_db import TestSession


class TestAuth(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.session = MagicMock(spec=Session)
    
    async def test_create_user(self):
        body = UserModel(
            email='example@gmail.com',
            password='admin'
            )
        result = await repo_auth.create_user(body=body, db=self.session)
        
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertIsNotNone(result.avatar)
    
    async def test_get_user_by_email_found(self):
        user = UserModel(email='example@gmail.com', password='admin')
        self.session.query().filter().first.return_value = user
        result = await repo_auth.get_user_by_email(user.email, self.session)
        self.assertEqual(result.email, user.email)
    
    async def test_get_user_by_email_not_found(self):
        user = User(email='example@gmail.com', password='admin')
        self.session.query().filter().first.return_value = None
        result = await repo_auth.get_user_by_email(user.email, self.session)
        self.assertIsNone(result)
    
    async def test_confirm_email(self):
        user = User(email='example@gmail.com', password='admin', confirmed=False)
        self.session.query().filter().first.return_value = user
        self.assertEqual(user.confirmed, False)
        await repo_auth.confirm_email(user.email, self.session)
        self.assertEqual(user.confirmed, True)


if __name__ == '__main__':
    unittest.main()