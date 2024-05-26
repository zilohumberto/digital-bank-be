from typing import Any, Dict

from application.models import Account
from application.repositories.persistence.entity_repository import EntityRepository


class AccountService:
    repository = None

    def __init__(self, repository: EntityRepository):
        self.repository = repository

    def create(self, data: Dict[str, Any]) -> Account:
        return self.repository.create(data=data)
