from app import db
from application.models import User, UserStatus
from application.repositories.persistence.entity_repository import EntityRepository
from application.services.user_service import UserService

repository = EntityRepository(model=User)
service = UserService(repository=repository)


def validate_users_created():
    users_created = service.repository.get_all(filters={"status": UserStatus.CREATED})
    if len(users_created) == 0:
        return {"total": 0}

    users_validated = []
    for user_created in users_created:
        # Simulate a validation automated process!!
        user_created = {
            "status": UserStatus.ACTIVE,
            "id": user_created.id
        }
        users_validated.append(user_created)

    db.session.bulk_update_mappings(User, users_validated)
    db.session.commit()
    return {"total": len(users_validated)}
