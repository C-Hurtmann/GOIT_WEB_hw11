import pytest
from unittest.mock import MagicMock, patch

from src.database.models import User
from src.services.auth import auth_service
from src.schemas import ContactModel


@pytest.fixture()
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr('src.routes.auth.send_email', mock_send_email)
    client.post('/api/auth/signup/', json=user)
    current_user: User = session.query(User).filter(User.email == user['email']).first()
    current_user.confirmed = True
    session.commit()
    response = client.post('api/auth/login', data={'username': user['email'], 'password': user['password']})
    
    data = response.json()
    return data['access_token']

def test_create_contact(client, token):
    with patch.object(auth_service, 'r') as mock:
        mock.get.return_value = None
        response = client.post(
            'api/contacts', 
            json={
                'first_name': 'Bob',
                'last_name': 'Ross',
                'email': 'example@gmail.com',
                'phone': '+380992968789',
                'birthday': '2020-03-29'
                },
            headers={'Authorization': f'Bearer {token}'}
            )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data['first_name'] == 'Bob'
        assert 'id' in data

def test_get_contact_found(client ,token):
    with patch.object(auth_service, 'r') as mock:
        mock.get.return_value = None
        response = client.get(
            'api/contacts/1',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['first_name'] == 'Bob'

def test_get_contact_not_found(client, token):
    with patch.object(auth_service, 'r') as mock:
        mock.get.return_value = None
        response = client.get(
            'api/contacts/2',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data['detail'] == 'Contact not found'

def test_get_contacts(client, token):
    with patch.object(auth_service, 'r') as mock:
        mock.get.return_value = None
        response = client.get(
            'api/contacts/?skip=0&limit=10',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert data[0]['first_name'] == 'Bob'
        assert 'id' in data[0]

def test_update_contact(client, token):
    with patch.object(auth_service, 'r') as mock:
        mock.get.return_value = None
        response = client.put(
            'api/contacts/1',
            json={
                'first_name': 'Bobby',
                'last_name': 'Ross',
                'email': 'example@gmail.com',
                'phone': '+380992968789',
                'birthday': '2020-03-29'
                },
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['first_name'] == 'Bobby'
        assert 'id' in data

def test_update_contact_not_found(client, token):
    with patch.object(auth_service, 'r') as mock:
        mock.get.return_value = None
        response = client.put(
            'api/contacts/2',
            json={
                'first_name': 'Bobbert',
                'last_name': 'Ross',
                'email': 'example@gmail.com',
                'phone': '+380992968789',
                'birthday': '2020-03-29'
                },
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data['detail'] == 'Contact not found'

def test_delete_contact(client, token):
    with patch.object(auth_service, 'r') as mock:
        mock.get.return_value = None
        response = client.delete(
            'api/contacts/1',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['first_name'] == 'Bobby'
        assert 'id' in data

def test_delete_contact_not_found(client, token):
    with patch.object(auth_service, 'r') as mock:
        mock.get.return_value = None
        response = client.delete(
            'api/contacts/2',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data['detail'] == 'Contact not found'