from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from src.database.models import User
from src.repository import users as repo_users
from tests.test_db import TestSession


class TestUsers(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.session = MagicMock(spec=Session)
    
    async def test_update_avatar(self):
        user = User(email='example@gmail.com', password='admin', avatar='')
        self.session.query().filter().first.return_value = user
        test_url = 'http://testurl.com'
        result = await repo_users.update_avatar(user.email, test_url, self.session)
        self.assertEqual(result.avatar, test_url)


if __name__ == '__main__':
    unittest.main()
    
    