# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Repositorio de usuarios. Partes: busqueda por email/id y creacion de usuario asociado a candidato.

"""User repository for authentication."""
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.entities import User


class UserRepository:
    """Data access layer for application users."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return (
            self.db.query(User)
            .options(joinedload(User.candidate))
            .filter(User.email == email)
            .first()
        )

    def get_by_id(self, user_id: int) -> Optional[User]:
        return (
            self.db.query(User)
            .options(joinedload(User.candidate))
            .filter(User.id == user_id)
            .first()
        )

    def create(self, email: str, hashed_password: str, candidate_id: int | None = None) -> User:
        user = User(email=email, hashed_password=hashed_password, candidate_id=candidate_id)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
