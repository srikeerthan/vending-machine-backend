import json
from typing import Optional

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.repositories.base import BaseRepository, ModelType, UpdateSchemaType
from app.models.users import Users
from app.schemas.users import UserInCreate, UserInUpdate
from app.db.session import get_db


class UsersRepository(BaseRepository[Users, UserInCreate, UserInUpdate]):
    """
    Repository to manipulate with the task.
    """

    def get_by_username(self, username: str) -> Optional[Users]:
        """
        Get user by `username` field.
        """
        return self.db.query(Users).filter(Users.username == username).first()

    def update(self, obj: ModelType, obj_update: UpdateSchemaType) -> ModelType:
        obj_data = jsonable_encoder(obj)
        update_data = obj_update.dict(exclude_unset=True)
        if update_data.get("roles"):
            update_data["roles"] = json.dumps(update_data["roles"])
        if update_data.get("password"):
            update_data["hashed_password"] = get_password_hash(password=update_data["password"])
        for field in obj_data:
            if field in update_data:
                setattr(obj, field, update_data[field])
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def disable_user(self, obj: Users) -> Users:
        obj.disabled = True
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    @staticmethod
    def is_active(user: Users) -> bool:
        """
        Check if user is active.
        """
        return not user.disabled


def get_users_repository(session: Session = Depends(get_db)) -> UsersRepository:
    return UsersRepository(db=session, model=Users)
