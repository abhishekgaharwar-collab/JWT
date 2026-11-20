from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth.jwt_handler import verify_token

router = APIRouter()

security = HTTPBearer()

students = [
    {"id": 1, "name": "Abhishek", "age": 22, "course": "Python"},
    {"id": 2, "name": "Rahul", "age": 23, "course": "FastAPI"}
]


# JWT Authentication
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    username = verify_token(token)

    if username is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return username


# GET - All Students
@router.get("/")
def get_students(
    current_user: str = Depends(get_current_user)
):

    return {
        "user": current_user,
        "students": students
    }


# GET - Student By ID
@router.get("/{student_id}")
def get_student(
    student_id: int,
    current_user: str = Depends(get_current_user)
):

    for student in students:
        if student["id"] == student_id:
            return student

    raise HTTPException(
        status_code=404,
        detail="Student not found"
    )


# POST - Add Student
@router.post("/")
def add_student(
    name: str,
    age: int,
    course: str,
    current_user: str = Depends(get_current_user)
):

    new_student = {
        "id": len(students) + 1,
        "name": name,
        "age": age,
        "course": course
    }

    students.append(new_student)

    return {
        "message": "Student added successfully",
        "student": new_student
    }
