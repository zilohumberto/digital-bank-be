from typing import Any, Dict

from application.models import User
from application.repositories.persistence.entity_repository import EntityRepository


class UserService:
    repository = None

    def __init__(self, repository: EntityRepository):
        self.repository = repository

    def create_user(self, data: Dict[str, Any]) -> User:
        return self.repository.create(data=data)

