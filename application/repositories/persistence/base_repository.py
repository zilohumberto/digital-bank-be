from app import db
from typing import Optional, Dict, Tuple, Any


class BaseRepository:
    """
    A base repository class to provide common CRUD operations for SQLAlchemy models.

    Attributes:
        model (db.Model): The SQLAlchemy model associated with this repository.
        entity_name (str): The name of the entity managed by this repository.
        black_list_fields (set): A set of field names to exclude from certain operations.
    """

    model = None
    entity_name = None
    black_list_fields = {"id", "creation_at", "last_updated"}

    def __init__(self, model: db.Model, black_list_fields: set = None):
        """
        Initializes the BaseRepository.

        Args:
            model (db.Model): The SQLAlchemy model associated with this repository.
            black_list_fields (set, optional): Fields to exclude from certain operations. Defaults to a set containing 'id', 'creation_at', 'last_updated'.
        """
        self.entity_name = model.__tablename__
        self.model = model
        self.black_list_fields = black_list_fields or self.black_list_fields

    def get(self, key: str, field: str = 'id') -> Optional[db.Model]:
        """
        Retrieves a single record by a given field.

        Args:
            key (str): The value to search for.
            field (str, optional): The field to search by. Defaults to 'id'.

        Returns:
            Optional[db.Model]: The retrieved record or None if not found.
        """
        raise NotImplementedError()

    def get_all(self, filters: Dict[str, Any], limit: int = 10, skip: int = 0) -> Optional[db.Model]:
        """
        Retrieves a multiple records by a given field.

        Args:
            key (str): The value to search for.
            field (str, optional): The field to search by. Defaults to 'id'.
            limit (int): limit of results
            skip (int): offset of results on query

        Returns:
            Optional[db.Model]: The retrieved record or None if not found.
        """
        raise NotImplementedError()

    def get_or_create(self, field: str, data: Dict[str, Any]) -> Tuple[Optional[db.Model], bool]:
        """
        Retrieves a record by a specified field if it exists, otherwise creates a new one.

        Args:
            field (str): The field to use for retrieving the record.
            data (Dict[str, Any]): The data to use for creating the record if it does not exist.

        Returns:
            Tuple[Optional[db.Model], bool]: A tuple containing the retrieved or created record and a boolean indicating
            whether the record was created (True) or retrieved (False).
        """
        raise NotImplementedError()

    def create(self, data: Dict[str, Any]) -> db.Model:
        """
        Creates a new record with the given data.

        Args:
            data (Dict[str, Any]): The data to use for creating the record.

        Returns:
            db.Model: The created record.
        """
        raise NotImplementedError()

    def update(self, data: Dict[str, Any], field: str = 'id') -> db.Model:
        """
        Updates an existing record with the given data.

        Args:
            data (Dict[str, Any]): The data to update the record with.
            field (str, optional): The field to search by. Defaults to 'id'.

        Returns:
            db.Model: The updated record.
        """
        raise NotImplementedError()

    def delete(self, key: str, field: str = 'id', is_soft_deleted: bool = True):
        """
        Deletes a record, either by performing a soft delete or a hard delete.

        Args:
            key (str): The value to search for.
            field (str, optional): The field to search by. Defaults to 'id'.
            is_soft_deleted (bool, optional): If True, performs a soft delete. Otherwise, performs a hard delete.
                Defaults to True.

        Raises:
            NotImplementedError: This method should be implemented by subclasses.
        """
        raise NotImplementedError()
