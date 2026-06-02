import pytest
from app import app
from unittest.mock import patch


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_homepage_loads(client):
    with patch('app.app.get_tasks', return_value=['Buy milk', 'Walk Dog']):
        response = client.get('/')
        assert response.status_code == 200
        assert b'Buy milk' in response.data


def test_add_task_redirects(client):
    with patch('app.app.add_task'):
        response = client.post('/add', data={'task': 'get milk'})
        assert response.status_code == 302
