from enum import Enum


class OperationType(Enum):
    DEPOSIT = "Deposit"  # no fee
    WITHDRAWAL = "Withdrawal"  # no fee
    TRANSFER = "Transfer"  # fee apply here when is between forex
    FEE = "Fee"


class UserStatus(Enum):
    CREATED = "created"  # user requests to create a profile, waiting for internal approval
    ACTIVE = "active"  # user activate and operative
    BLOCKED = "blocked"  # user blocked for complaints reasons (internal only)
    INACTIVE = "inactive"  # user inactive for X days without movements

class AccountStatus(Enum):
    CREATED = "created"  # user requests to create an account, waiting for internal approval
    ACTIVE = "active"  # account active and operative for transactions
    BLOCKED = "blocked"  # account blocked by internal requests (internal only)
    INACTIVE = "inactive"  # inactive for X days without movements


class OperationStatus(Enum):
    CREATED = "created"  # created the single row without impacting the balance
    PENDING = "pending"  # take by batch to be processed
    CANCELLED = "cancelled"  # cancelled by the user
    FAILED = "failed"  # failed while was trying to operate
    DONE = "done"  # finally impacted the balance -> Account
