from starlette.testclient import TestClient

from app.main import app

url = "/users"


def test_status():
    client = TestClient(app)
    response = client.get(url)

    assert response.status_code == 200
    assert response.url == "http://testserver/users"


def test_has_correct_context():
    client = TestClient(app)
    response = client.get(url)

    assert "request" in response.context


def test_template():
    client = TestClient(app)
    response = client.get(url)

    assert response.template.name == "users.html"
