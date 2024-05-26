from typing import Any, Dict

from application.models import Transaction
from application.repositories.persistence.entity_repository import EntityRepository


class TransactionService:
    repository = None

    def __init__(self, repository: EntityRepository):
        self.repository = repository

    def create(self, data: Dict[str, Any]) -> Transaction:
        return self.repository.create(data)

