from backend.models.user import User
import uuid

def get_current_user():
    return User(id=uuid.uuid4(), username="testuser", email="test@test.com", hashed_password="password")
