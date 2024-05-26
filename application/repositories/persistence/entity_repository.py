from typing import Optional, Dict, Tuple, Any, List
from sqlalchemy import select, and_

from app import db
from application.repositories.persistence.base_repository import BaseRepository


class EntityRepository(BaseRepository):
    """
    A repository class to provide specific CRUD operations for a SQLAlchemy model.

    Inherits common CRUD operations from BaseRepository and implements specific logic for
    get, get_or_create, create, update, and delete operations.
    """

    def get(self, key: str, field: str = 'id') -> Optional[db.Model]:
        """
        Retrieves a single record by a given field.

        Args:
            key (str): The value to search for.
            field (str, optional): The field to search by. Defaults to 'id'.

        Returns:
            Optional[db.Model]: The retrieved record or None if not found.
        """
        stmt = select(self.model).where(getattr(self.model, field) == key)
        result = db.session.execute(stmt).scalar()
        return result

    def get_all(self, filters: Dict[str, Any], limit: int = 10, skip: int = 0) -> List[db.Model]:
        """
        Retrieves a multiple records by a given field.

        Args:
            filters (map): key and value to be filter on
            limit (int): limit of results
            skip (int): offset of results on query

        Returns:
            Optional[db.Model]: The retrieved record or None if not found.
        """
        filters_query = []
        for field, value in filters.items():
            if hasattr(self.model, field):
                filters_query.append(
                    getattr(self.model, field) == value
                )
        if filters_query:
            stmt = select(self.model).where(and_(*filters_query))
        else:
            stmt = select(self.model)
        stmt = stmt.order_by(self.model.last_updated.desc()).limit(limit).offset(skip)
        results = db.session.execute(stmt).scalars().all()
        return results

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
        object_instance = self.get(key=data[field], field=field)
        is_created = False
        if object_instance is None:
            object_instance = self.create(data)
            is_created = True
        return object_instance, is_created

    def create(self, data: Dict[str, Any]) -> db.Model:
        """
        Creates a new record with the given data.

        Args:
            data (Dict[str, Any]): The data to use for creating the record.

        Returns:
            db.Model: The created record.
        """
        object_instance = self.model(**data)
        db.session.add(object_instance)
        db.session.commit()
        return object_instance

    def update(self, data: Dict[str, Any], field: str = 'id') -> db.Model:
        """
        Updates an existing record with the given data.

        Args:
            data (Dict[str, Any]): The data to update the record with.
            field (str, optional): The field to search by. Defaults to 'id'.

        Returns:
            db.Model: The updated record.

        Raises:
            ValueError: If the record is not found.
        """
        object_instance = self.get(key=data[field], field=field)
        if object_instance is None:
            raise ValueError(f"{self.entity_name} not found for {field}={data[field]}")

        for field, value in data.items():
            if hasattr(object_instance, field) and field not in self.black_list_fields:
                setattr(object_instance, field, value)

        db.session.add(object_instance)
        db.session.commit()
        return object_instance

    def delete(self, pk: str, field: str = 'id', is_soft_delete: bool = True):
        """
        Deletes a record, either by performing a soft delete or a hard delete.

        Args:
            pk (str): The value to search for.
            field (str, optional): The field to search by. Defaults to 'id'.
            is_soft_delete (bool, optional): If True, performs a soft delete. Otherwise, performs a hard delete. Defaults to True.

        Raises:
            ValueError: If the record is not found for hard delete.
        """
        if is_soft_delete:
            data = {"is_deleted": True, field: pk}
            self.update(data=data, field=field)
        else:
            object_instance = self.get(key=pk, field=field)
            if object_instance is None:
                raise ValueError(f"{self.entity_name} not found for {field}={pk}")
            db.session.delete(object_instance)
            db.session.commit()
