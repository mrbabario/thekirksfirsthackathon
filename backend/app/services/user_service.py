from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.schemas.auth import RegisterRequest
from backend.app.core.security import hash_password


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:

    statement = select(User).where(
        User.email == email
    )

    return db.scalar(statement)


def create_user(
    db: Session,
    user_data: RegisterRequest,
) -> User:

    new_user = User(
        full_name=user_data.full_name.strip(),
        email=user_data.email.lower().strip(),
        password_hash=hash_password(user_data.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
