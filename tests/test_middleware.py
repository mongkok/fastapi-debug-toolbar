from fastapi import status

from .testclient import TestClient


def test_sync(client: TestClient) -> None:
    response = client.get("/sync")
    assert response.status_code == status.HTTP_200_OK


def test_async(client: TestClient) -> None:
    response = client.get("/async")
    assert response.status_code == status.HTTP_200_OK


def test_404(client: TestClient) -> None:
    response = client.get("/404")
    assert response.status_code == status.HTTP_404_NOT_FOUND
