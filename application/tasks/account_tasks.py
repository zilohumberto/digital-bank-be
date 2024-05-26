from app import db
from application.models import Account, AccountStatus
from application.repositories.persistence.entity_repository import EntityRepository
from application.services.account_service import AccountService

repository = EntityRepository(model=Account)
service = AccountService(repository=repository)


def validate_accounts_created():
    accounts_created = service.repository.get_all(filters={"status": AccountStatus.CREATED})
    if len(accounts_created) == 0:
        return {"total": 0}

    accounts_validated = []
    for user_created in accounts_created:
        # Simulate a validation automated process!!
        user_created = {
            "status": AccountStatus.ACTIVE,
            "id": user_created.id
        }
        accounts_validated.append(user_created)

    db.session.bulk_update_mappings(Account, accounts_validated)
    db.session.commit()
    return {"total": len(accounts_validated)}
