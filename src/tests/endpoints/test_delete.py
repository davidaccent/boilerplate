from starlette.testclient import TestClient
from starlette_auth.tables import User

from app.main import app

login_data = {"email": "ted@example.com", "password": "password"}


def get_user(email="ted@example.com"):
    user = User(email=email, first_name="Ted", last_name="Bundy")
    user.set_password("password")
    user.save()
    url = app.url_path_for("user_delete", user_id=user.id)

    return user, url


def test_login_required():
    _, url = get_user()
    client = TestClient(app)
    response = client.get(url)
    assert response.status_code == 200
    assert response.url == "http://testserver/auth/login"


def test_response():
    _, url = get_user()
    with TestClient(app) as client:
        client.post("/auth/login", data=login_data)
        response = client.get(url)
        assert response.template.name == "delete.html"
        assert response.status_code == 200
        assert response.url == f"http://testserver{url}"


def test_has_correct_context():
    _, url = get_user()
    with TestClient(app) as client:
        client.post("/auth/login", data=login_data)
        response = client.get(url)

        assert "request" in response.context


def test_template():
    _, url = get_user()
    with TestClient(app) as client:
        client.post("/auth/login", data=login_data)
        response = client.get(url)

        assert response.template.name == "delete.html"


def test_delete_disabled_single_user():
    _, url = get_user()
    with TestClient(app) as client:
        client.post("/auth/login", data=login_data)
        response = client.post(url)

        assert User.query.count() == 1
        assert response.status_code == 302


def test_post_delete():
    _, url = get_user()
    get_user("ted2@example.com")
    assert User.query.count() == 2
    with TestClient(app) as client:
        client.post("/auth/login", data=login_data)
        response = client.post(url)

        # after saving page should be redirt to users screen
        assert User.query.count() == 1
        assert response.status_code == 302
        assert response.next.url == f"http://testserver/users"
