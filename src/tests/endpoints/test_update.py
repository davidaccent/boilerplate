from starlette.testclient import TestClient
from starlette_auth.tables import User

from app.main import app


def get_user():
    user = User(email="ted@example.com", first_name="Ted", last_name="Bundy")
    user.save()
    url = app.url_path_for("user_update", user_id=user.id)

    return user, url


def test_response():
    _, url = get_user()
    with TestClient(app) as client:
        response = client.get(url)
        assert response.status_code == 200
        assert response.template.name == "update.html"
        assert response.url == f"http://testserver{url}"


def test_has_correct_context():
    _, url = get_user()
    with TestClient(app) as client:
        response = client.get(url)
        assert "request" in response.context


def test_template():
    _, url = get_user()
    with TestClient(app) as client:
        response = client.get(url)
        assert response.template.name == "update.html"


def test_post_update():
    user, url = get_user()
    with TestClient(app) as client:
        response = client.post(
            url,
            data={
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "is_active": user.is_active,
            },
        )

        # after saving page should be redirt to users screen
        assert response.status_code == 302
        assert response.next.url == f"http://testserver/users"
