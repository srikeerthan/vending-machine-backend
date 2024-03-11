import base64
from collections import defaultdict

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app

# Set up the TestClient
client = TestClient(app)

# Set up the in-memory SQLite database for testing
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to override the get_db dependency in the main app
def override_get_db():
    database = TestingSessionLocal()
    yield database
    database.close()


app.dependency_overrides[get_db] = override_get_db

# Creates all the tables from the declared models for testing
Base.metadata.create_all(bind=engine)

test_seller3_token, test_seller2_token, test_seller1_token = "", "", ""
test_buyer1_token, test_buyer2_token, test_buyer3_token = "", "", ""

product_name_id_map = dict()


def get_oauth2_auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_create_user():
    response = client.post(
        "/api/v1/users",
        json={"username": "seller3", "email": "seller3@example.com", "full_name": "seller3", "roles": ["seller"],
              "password": "string"}
    )
    assert response.status_code == 200, response.text
    data = response.json()['data']
    assert data["username"] == "seller3"
    assert data["email"] == "seller3@example.com"
    assert data["full_name"] == "seller3"
    assert data["roles"] == ["seller"]
    assert "id" in data


def test_create_seller_user():
    response = client.post(
        "/api/v1/users",
        json={"username": "seller2", "email": "seller2@example.com", "full_name": "seller2", "roles": ["seller"],
              "password": "string"}
    )
    assert response.status_code == 200, response.text
    data = response.json()['data']
    assert data["username"] == "seller2"
    assert data["email"] == "seller2@example.com"
    assert data["full_name"] == "seller2"
    assert data["roles"] == ["seller"]
    assert "id" in data


def test_create_seller1_user():
    response = client.post(
        "/api/v1/users",
        json={"username": "seller1", "email": "seller1@example.com", "full_name": "seller1", "roles": ["seller"],
              "password": "string"}
    )
    assert response.status_code == 200, response.text
    data = response.json()['data']
    assert data["username"] == "seller1"
    assert data["email"] == "seller1@example.com"
    assert data["full_name"] == "seller1"
    assert data["roles"] == ["seller"]
    assert "id" in data


def test_create_existing_user():
    response = client.post(
        "/api/v1/users",
        json={"username": "seller3", "email": "seller3@example.com", "full_name": "seller3", "roles": ["seller"],
              "password": "string"}
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["type"] == "UserAlreadyExistException"


def test_create_user_with_invalid_roles():
    response = client.post(
        "/api/v1/users",
        json={"username": "seller3", "email": "seller3@example.com", "full_name": "seller3", "roles": ["admin"],
              "password": "string"}
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["type"] == "InvalidInputDataException"


def test_login_user():
    response = client.post("/api/v1/users/login", json={"username": "seller3", "password": "string"})
    assert response.status_code == 200, response.text
    data = response.json()['data']
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    global test_seller3_token
    test_seller3_token = data["access_token"]


def test_login_seller2_user():
    response = client.post("/api/v1/users/login", json={"username": "seller2", "password": "string"})
    assert response.status_code == 200, response.text
    data = response.json()['data']
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    global test_seller2_token
    test_seller2_token = data["access_token"]


def test_login_seller1_user():
    response = client.post("/api/v1/users/login", json={"username": "seller1", "password": "string"})
    assert response.status_code == 200, response.text
    data = response.json()['data']
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    global test_seller1_token
    test_seller1_token = data["access_token"]


def test_read_user():
    response = client.get("/api/v1/users/seller3", headers=get_oauth2_auth_header(test_seller3_token))
    assert response.status_code == 200, response.text
    data = response.json()['data']
    assert data["username"] == "seller3"
    assert data["email"] == "seller3@example.com"
    assert data["full_name"] == "seller3"
    assert data["roles"] == ["seller"]
    assert "id" in data


def test_read_user_not_exists():
    response = client.get("/api/v1/users/seller2", headers=get_oauth2_auth_header(test_seller3_token))
    assert response.status_code == 403, response.text
    data = response.json()
    assert data["type"] == "UserPermissionException"


def test_update_user():
    response = client.put("/api/v1/users/seller3", headers=get_oauth2_auth_header(test_seller3_token),
                          json={"username": "seller3", "email": "seller3@example.com", "full_name": "seller3",
                                "roles": ["seller"]})
    assert response.status_code == 200, response.text
    data = response.json()['data']
    assert data["username"] == "seller3"
    assert data["email"] == "seller3@example.com"
    assert data["full_name"] == "seller3"
    assert data["roles"] == ["seller"]
    assert "id" in data


def test_update_user_with_other_existing_user():
    response = client.put("/api/v1/users/seller3", headers=get_oauth2_auth_header(test_seller3_token),
                          json={"username": "seller2", "email": "seller3@example.com", "full_name": "seller3",
                                "roles": ["seller"]})
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["type"] == "UserAlreadyExistException"
    assert data["message"] == "User with username: `seller2` already exists"


def test_delete_user_with_other_user_credentials():
    response = client.delete("/api/v1/users/seller1", headers=get_oauth2_auth_header(test_seller3_token))
    assert response.status_code == 403, response.text
    data = response.json()
    assert data["type"] == "UserPermissionException"


def test_delete_user():
    response = client.delete("/api/v1/users/seller1", headers=get_oauth2_auth_header(test_seller1_token))
    assert response.status_code == 200, response.text
    data = response.json()['data']
    assert data["username"] == "seller1"
    assert data["email"] == "seller1@example.com"
    assert data["full_name"] == "seller1"
    assert data["roles"] == ["seller"]
    assert "id" in data


def test_create_products():
    response = client.post("/api/v1/products", headers=get_oauth2_auth_header(test_seller3_token), json={
        "name": "bourbon",
        "price": 2.50,
        "quantity": 7
    })
    assert response.status_code == 200, response.text
    data = response.json()['data']
    assert data["name"] == "bourbon"
    assert data["price"] == 2.50
    assert data["quantity"] == 7
    assert "id" in data
    product_name_id_map[data["name"]] = data["id"]


def test_create_product_lays():
    response = client.post("/api/v1/products", headers=get_oauth2_auth_header(test_seller3_token), json={
        "name": "lays",
        "price": 1.30,
        "quantity": 10
    })
    assert response.status_code == 200, response.text
    data = response.json()['data']
    assert data["name"] == "lays"
    assert data["price"] == 1.30
    assert data["quantity"] == 10
    assert "id" in data
    product_name_id_map[data["name"]] = data["id"]


def test_create_products_with_seller2():
    response = client.post("/api/v1/products", headers=get_oauth2_auth_header(test_seller2_token), json={
        "name": "5star",
        "price": 2.50,
        "quantity": 7
    })
    assert response.status_code == 200, response.text
    data = response.json()['data']
    assert data["name"] == "5star"
    assert data["price"] == 2.50
    assert data["quantity"] == 7
    assert "id" in data
    product_name_id_map[data["name"]] = data["id"]


def test_create_product_bingo_with_seller2():
    response = client.post("/api/v1/products", headers=get_oauth2_auth_header(test_seller2_token), json={
        "name": "bingo",
        "price": 1.30,
        "quantity": 9
    })
    assert response.status_code == 200, response.text
    data = response.json()['data']
    assert data["name"] == "bingo"
    assert data["price"] == 1.30
    assert data["quantity"] == 9
    assert "id" in data
    product_name_id_map[data["name"]] = data["id"]


def test_create_products_with_existing_name():
    response = client.post("/api/v1/products", headers=get_oauth2_auth_header(test_seller3_token), json={
        "name": "bourbon",
        "price": 2.50,
        "quantity": 7
    })
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["type"] == "ProductAlreadyExistsException"


def test_get_product_details():
    response = client.get("/api/v1/products/{}".format(product_name_id_map.get("bourbon")))
    assert response.status_code == 200, response.text
    data = response.json()['data']
    assert data["name"] == "bourbon"
    assert data["price"] == 2.50
    assert data["quantity"] == 7


def test_get_product_details_with_invalid_id():
    response = client.get("/api/v1/products/00000000")
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["type"] == "ProductNotFoundException"


def test_get_products_with_pagination():
    response = client.get("/api/v1/products", params={"page": 1, "per_page": 1})
    assert response.status_code == 200, response.text
    data = response.json()['data']
    print(data)
