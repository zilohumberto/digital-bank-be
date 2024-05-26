from typing import List

from app import db
from application.models import Transaction, Account, OperationStatus, OperationType, AccountStatus, UserStatus
from application.repositories.persistence.entity_repository import EntityRepository
from application.services.transaction_service import TransactionService
from application.services.api_rate_service import ApiRateService
from settings import FEE_PERCENTAGE


repository_transaction = EntityRepository(model=Transaction)
service_transaction = TransactionService(repository=repository_transaction)
repository_account = EntityRepository(model=Account)
service_account = TransactionService(repository=repository_account)
api_rate_Service = ApiRateService()


def search_transaction_created() -> List[Transaction]:
    transactions_created = service_transaction.repository.get_all(filters={"operation_status": OperationStatus.CREATED})
    for transaction_created in transactions_created:
        data = {"operation_status": OperationStatus.PENDING, "id": transaction_created.id}
        transaction_created.operation_status = OperationStatus.PENDING
        service_transaction.repository.update(data)
        yield transaction_created
    return None


def execute_transactions(iterator=None):
    if iterator is None:
        iterator = search_transaction_created()
    data = {
        "total": 0,
        "success": 0,
        "failed": 0,
    }
    for transaction in iterator:
        if transaction is None:
            break
        data["total"] += 1
        transaction_is_done: bool = False
        transaction_total: float = 0.0
        try:
            origin_account_instance = service_account.repository.get(key=transaction.origin_account_id)
            destination_account_instance = service_account.repository.get(key=transaction.destination_account_id)
            # both user and account of destination have to be active!
            if destination_account_instance.status == AccountStatus.ACTIVE and destination_account_instance.user.status == UserStatus.ACTIVE:
                if transaction.operation == OperationType.DEPOSIT:
                    # Manual/external process Validate deposit is in out account so we proceed
                    after_deposit_total = round(origin_account_instance.total + transaction.amount, 4)
                    service_account.repository.update(
                        data=dict(
                            id=origin_account_instance.id,  # intentionally ignored destination_account_id
                            total=after_deposit_total,
                        )
                    )
                    transaction_total = after_deposit_total
                    transaction_is_done = True
                elif transaction.operation == OperationType.WITHDRAWAL:
                    # Manual/external process execute transfer from our bank to another!
                    new_amount = round(origin_account_instance.total - transaction.amount, 4)
                    if new_amount >= 0:
                        service_account.repository.update(
                            data=dict(
                                id=origin_account_instance.id,  # intentionally ignored destination_account_id
                                total=new_amount,
                            )
                        )
                        transaction_is_done = True
                        transaction_total = new_amount
                elif transaction.operation == OperationType.TRANSFER:
                    # if it's transfer between currencies we apply charge
                    is_transfer_between_currencies = origin_account_instance.currency_name != destination_account_instance.currency_name
                    conversion_rate = api_rate_Service.get_rate(
                        origin_currency_name=origin_account_instance.currency_name,
                        destination_currency_name=destination_account_instance.currency_name
                    )
                    transaction_fee = transaction.amount * FEE_PERCENTAGE if is_transfer_between_currencies else 0.0
                    fee_total = round(origin_account_instance.total - transaction_fee, 4)
                    # sender has enough money to transfer? balance - amount of transaction + fee (if apply)
                    if origin_account_instance.total - (transaction.amount + transaction_fee) >= 0:
                        # destination receive: total of money (already have) + (transaction amount * conversion rate)
                        destination_new_total = round(
                                destination_account_instance.total + (transaction.amount * conversion_rate), 4
                        )
                        # with fee
                        transaction_total = round(origin_account_instance.total - (transaction.amount + transaction_fee), 4)
                        #  CREATE a transaction that do not affect the balance but the user will see it in his movements
                        reference = f"Exchange from {origin_account_instance.currency_name}" if is_transfer_between_currencies else f"Transferencia regular"
                        transaction_transfer = Transaction(
                            amount=round(transaction.amount * conversion_rate, 4),
                            total=destination_new_total,
                            operation=OperationType.TRANSFER,
                            operation_status=OperationStatus.DONE,
                            origin_account_id=origin_account_instance.id,
                            destination_account_id=destination_account_instance.id,
                            user_id=destination_account_instance.user_id,
                            currency_name=destination_account_instance.currency_name,
                            linked_transaction_id=transaction.linked_transaction_id,
                            reference=reference
                        )
                        db.session.add(transaction_transfer)
                        accounts = [
                            {
                                "id": origin_account_instance.id,
                                "total" : transaction_total,
                             },
                            {
                                "id": destination_account_instance.id,
                                "total": destination_new_total
                            }
                        ]
                        db.session.bulk_update_mappings(Account, accounts)
                        db.session.commit()
                        if is_transfer_between_currencies:
                            # create transaction fee so the user known what was charged
                            transaction_fee_instance = Transaction(
                                amount=transaction_fee,
                                total=fee_total,
                                operation = OperationType.FEE,
                                operation_status = OperationStatus.DONE,
                                origin_account_id =origin_account_instance.id,
                                destination_account_id =origin_account_instance.id,
                                user_id=origin_account_instance.user_id,
                                currency_name=origin_account_instance.currency_name,
                                linked_transaction_id=transaction.linked_transaction_id,
                            )
                            db.session.add(transaction_fee_instance)
                            db.session.commit()
                        
                        transaction_is_done = True
            else:
                # type is not valid
                pass
        except Exception as e:
            print(e)  # TODO: log error!
            db.session.rollback()

        if transaction_is_done:
            transaction.total = transaction_total
            transaction.operation_status = OperationStatus.DONE
            data["success"] += 1
        else:
            transaction.operation_status = OperationStatus.FAILED
            data["failed"] += 1
        db.session.add(transaction)
        db.session.commit()

    return data