import pytest
import sqlalchemy
from fastapi.testclient import TestClient

from db import TEST_DATABASE_URL, metadata
from main import app
from settings import (DATABASE_URL, FILE, PK, PK_16, TEST_ROOT, USER_TEST,
                      USER_UPDATE_TEST)


class Cache:
    headers = {"Authorization": "Bearer {}"}
    user = {}


@pytest.fixture(autouse=True, scope="session")
def create_test_database():
    """Создаем таблицы."""
    engine = sqlalchemy.create_engine(TEST_DATABASE_URL)
    metadata.create_all(engine)
    yield
    metadata.drop_all(engine)
    message = "Не удалось подключится к PostgreSQL"
    assert DATABASE_URL == TEST_DATABASE_URL, message


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
    data = {"username": "wrong data", "password": "wrong data"}
    response = client.post('/users/login', data=data)
    assert response.status_code == 400

    response = client.post('/users/login', data=USER_TEST)
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    refresh_token = response.json()["refresh_token"]
    assert response.json() == {
        "access_token": access_token, "refresh_token": refresh_token
    }
    Cache.headers = {"Authorization": "Bearer {}".format(access_token)}


def test_get_me(client):
    """Проверяет информацию авторизированного пользователя."""
    response = client.get("/users/me", headers=Cache.headers)
    assert response.status_code == 200
    for index, value in response.json().items():
        if index == 'timestamp':
            pass
        else:
            assert value == PK if index == "id" else value == USER_TEST[index]
    Cache.user = response.json()


def test_post_user_update(client):
    """Проверка обновления полей юзера."""
    response = client.post(
        "/users/update", json=USER_UPDATE_TEST, headers=Cache.headers)
    two_result = response.json()
    assert response.status_code == 200

    response = client.get("/users/me", headers=Cache.headers)
    assert response.status_code == 200
    for index, value in response.json().items():
        if index in USER_UPDATE_TEST:
            assert value == two_result[index]
            assert value == USER_UPDATE_TEST[index]
            assert value != Cache.user[index]
        else:
            assert value == Cache.user[index]


def test_post_frames_check(client):
    """Проверяет формат файла и лимит в 15 изображений."""

    def _get_image_file(name=f'{FILE}png'):
        """Открывает нужный файл."""
        return "files", open(f"{TEST_ROOT}/{name}", "rb")

    response = client.post("frames/", headers=Cache.headers)
    assert response.status_code == 422

    response = client.post(
        "frames/", files=[_get_image_file()], headers=Cache.headers
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

    files = [_get_image_file(name=f"{FILE}jpg") for _ in range(PK_16)]
    response = client.post("/frames/", files=files, headers=Cache.headers)
    assert response.status_code == 200
    assert response.json() == {
        "message": {f"{FILE}jpg": {"status": 201}},
        "error": {"limit": "You have submitted more than 15 images"}
    }


def test_get_frames_check(client):
    """Проверяет наличие и отсутствие файла."""
    response = client.get(f"frames/{PK}", headers=Cache.headers)
    assert response.status_code == 200
    assert response.json()["id"] == PK

    response = client.get("frames/0", headers=Cache.headers)
    assert response.status_code == 404
    assert response.json() == {'message': 'No file'}


def test_delete_frames_check(client):
    """Проверяет удаление 15 файлов и 1 несуществующего."""
    for i in range(1, PK_16):
        response = client.delete(f"frames/{i}", headers=Cache.headers)
        assert response.status_code == 200
        assert response.json() == {"message": "File deleted"}

    response = client.delete(f"frames/{PK}", headers=Cache.headers)
    assert response.status_code == 404
    assert response.json() == {'message': 'No file'}
