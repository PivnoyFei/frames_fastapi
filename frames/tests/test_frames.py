import sys

from fastapi.testclient import TestClient
from main import app
from settings import TEST_ROOT

sys.path.append("..")
client = TestClient(app)

PK, PK_16 = 1, 16
FILE = "tolstoy"


def test_post_frames_check():
    """Проверяет формат файла и лимит в 15 изображений."""
    response = client.post("/frames/")
    assert response.status_code == 422

    files = [("files", open(f"{TEST_ROOT}/{FILE}.png", "rb"))]
    response = client.post("/frames/", files=files)
    assert response.status_code == 200
    assert response.json() == {
        "message": {}, "error": {f"{FILE}.png": {
            "message": "File extension not jpg or jpeg", "status": 400}}}

    files = [("files", open(f"{TEST_ROOT}/{FILE}.jpg", "rb")) for _ in range(PK_16)]
    response = client.post("/frames/", files=files)
    assert response.status_code == 200
    r = response.json()
    assert r == {
        "message": {f"{FILE}.jpg": {"status": 201}}, "error": {
            "limit": "You have submitted more than 15 images"}}


def test_get_frames_check():
    """Проверяет наличие и отсутствие изображения."""
    response = client.get(f"/frames/{PK}")
    assert response.status_code == 200
    assert response.json()["id"] == PK

    response = client.get("/frames/0")
    assert response.status_code == 404
    assert response.json() == {'message': 'No file'}


def test_delete_frames_check():
    """Проверяет удаление 15 файлов и 1 несуществующего."""
    for i in range(1, PK_16):
        response = client.delete(f"/frames/{i}")
        assert response.status_code == 200
        assert response.json() == {"message": "File deleted"}

    response = client.delete(f"/frames/{PK}")
    assert response.status_code == 404
    assert response.json() == {'message': 'No file'}
