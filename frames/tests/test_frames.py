import pytest
import sqlalchemy
from fastapi.testclient import TestClient

from db import metadata
from main import app
from settings import DATABASE_URL, FILE, PK, PK_16, TEST_ROOT, USER_TEST


@pytest.fixture(autouse=True, scope="session")
def create_test_database():
    """Создаем таблицы."""
    engine = sqlalchemy.create_engine(DATABASE_URL)
    metadata.create_all(engine)
    yield
    metadata.drop_all(engine)


@pytest.fixture()
def client():
    """Подключаемся к БД."""
    with TestClient(app) as client:
        yield client


def test_post_user_create(client):
    """Создаем юзера."""
    response = client.post("/users/signup", json=USER_TEST)
    assert response.status_code == 200
    assert len(response.json()) == 4
    for index, value in response.json().items():
        assert value == USER_TEST[index]


def test_post_login(client):
    """Тестирует авторизацию с неправильными и правильными данными."""
    response = client.post(
        '/users/login', data={"username": "u", "password": "p"}
    )
    assert response.status_code == 400

    data = {
        "username": USER_TEST["username"],
        "password": USER_TEST["password"]
    }
    response = client.post('/users/login', data=data)
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    refresh_token = response.json()["refresh_token"]
    assert response.json() == {
        "access_token": access_token, "refresh_token": refresh_token
    }
    global headers
    headers = {"Authorization": "Bearer {}".format(access_token)}


def test_get_me(client):
    """Проверяет информацию авторизированного пользователя."""
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    for index, value in response.json().items():
        assert value == PK if index == "id" else value == USER_TEST[index]


def test_post_frames_check(client):
    """Проверяет формат файла и лимит в 15 изображений."""

    def __get_image_file(name=f'{FILE}png'):
        """Открывает нужный файл."""
        return ("files", open(f"{TEST_ROOT}/{name}", "rb"))

    response = client.post("frames/", headers=headers)
    assert response.status_code == 422

    response = client.post(
        "frames/", files=[__get_image_file()], headers=headers
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": {},
        "error": {
            f"{FILE}png": {
                "message": "File extension not jpg or jpeg",
                "status": 400
            }
        }
    }

    files = [__get_image_file(name=f"{FILE}jpg") for _ in range(PK_16)]
    response = client.post("/frames/", files=files, headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "message": {f"{FILE}jpg": {"status": 201}},
        "error": {"limit": "You have submitted more than 15 images"}
    }


def test_get_frames_check(client):
    """Проверяет наличие и отсутствие файла."""
    response = client.get(f"frames/{PK}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == PK

    response = client.get("frames/0", headers=headers)
    assert response.status_code == 404
    assert response.json() == {'message': 'No file'}


def test_delete_frames_check(client):
    """Проверяет удаление 15 файлов и 1 несуществующего."""
    for i in range(1, PK_16):
        response = client.delete(f"frames/{i}", headers=headers)
        assert response.status_code == 200
        assert response.json() == {"message": "File deleted"}

    response = client.delete(f"frames/{PK}", headers=headers)
    assert response.status_code == 404
    assert response.json() == {'message': 'No file'}
