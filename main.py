from fastapi import FastAPI

from routers import auth, students
from middleware.logger import log_requests

app = FastAPI(title="Student Management System")

# Middleware
app.middleware("http")(log_requests)

# Authentication Router
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# Student Router
app.include_router(
    students.router,
    prefix="/students",
    tags=["Students"]
)

@app.get("/")
def home():
    return {"message": "Welcome to Student Management System"}
