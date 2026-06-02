import pytest
from app.app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_homepage_loads(client):
    response = client.get('/')
    assert response.status_code == 200


def test_add_task_redirects(client):
    response = client.post('/add', data={'task': 'get milk'})
    assert response.status_code == 302
