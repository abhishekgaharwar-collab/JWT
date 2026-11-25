
import pytest
from fastapi.testclient import TestClient

from main import app
from routers.auth import users
from routers.students import students

client = TestClient(app)


# Reset in-memory data before every test
@pytest.fixture(autouse=True)
def reset_data():
    users.clear()

    students.clear()
    students.extend([
        {"id": 1, "name": "Abhishek", "age": 22, "course": "Python"},
        {"id": 2, "name": "Rahul", "age": 23, "course": "FastAPI"}
    ])

    yield


# Reusable authenticated user
@pytest.fixture
def auth_token():
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "password": "testpassword"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "testpassword"
        }
    )

    return response.json()["access_token"]


# 1. Homepage Test
def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to Student Management System"
    }


# 2. Successful Registration
def test_register_user():
    response = client.post(
        "/auth/register",
        json={
            "username": "abhishek",
            "password": "password123"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "User registered successfully"


# 3. Duplicate Registration
def test_duplicate_registration():
    payload = {
        "username": "abhishek",
        "password": "password123"
    }

    client.post("/auth/register", json=payload)

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"


# 4. Successful Login
def test_login_success():
    payload = {
        "username": "abhishek",
        "password": "password123"
    }

    client.post("/auth/register", json=payload)

    response = client.post("/auth/login", json=payload)

    assert response.status_code == 200
    assert response.json()["message"] == "Login successful"
    assert response.json()["token_type"] == "bearer"
    assert "access_token" in response.json()


# 5. Login With Incorrect Password
def test_login_invalid_password():
    client.post(
        "/auth/register",
        json={
            "username": "abhishek",
            "password": "password123"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "abhishek",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


# 6. Get All Students With Valid JWT
def test_get_students(auth_token):
    response = client.get(
        "/students/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    assert response.json()["user"] == "testuser"
    assert len(response.json()["students"]) == 2


# 7. Access Students Without JWT
def test_students_without_token():
    response = client.get("/students/")

    assert response.status_code == 401


# 8. Access Students With Invalid JWT
def test_students_with_invalid_token():
    response = client.get(
        "/students/",
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


# 9. Get Student By ID
def test_get_student_by_id(auth_token):
    response = client.get(
        "/students/1",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Abhishek"


# 10. Student Not Found
def test_student_not_found(auth_token):
    response = client.get(
        "/students/999",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"


# 11. Add Student
def test_add_student(auth_token):
    response = client.post(
        "/students/",
        params={
            "name": "Amit",
            "age": 24,
            "course": "Docker"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Student added successfully"
    assert response.json()["student"]["name"] == "Amit"


# 12. Middleware Header Test
def test_middleware_header():
    response = client.get("/")

    assert response.status_code == 200
    assert "X-Process-Time" in response.headers
