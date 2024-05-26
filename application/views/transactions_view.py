from app import app
from flask import request, jsonify, g
from uuid import uuid4

from application.models import Transaction, OperationStatus
from application.repositories.persistence.entity_repository import EntityRepository
from application.services.transaction_service import TransactionService
from application.validation_schemas import TransactionSchema
from application.authentication import token_required
from application.tasks.transaction_tasks import execute_transactions
from application.services.auth_service import AuthService
from application.services.api_rate_service import ApiRateService

repository = EntityRepository(model=Transaction)
service = TransactionService(repository=repository)
auth_service = AuthService()
api_rate_service = ApiRateService()


def _get_transaction_input():
    filters = {}
    if 'user_id' in request.args:
        filters["user_id"] = request.args.get('user_id')
    if "operation_status" in request.args:
        operation_status = request.args.get('operation_status')
        filters["operation_status"] = OperationStatus[operation_status.upper()]
    currency_name = request.args.get('currency_name')
    if currency_name is None:
        raise ValueError("currency_name is not provide")
    else:
        filters["currency_name"] = currency_name
    return filters


@app.route("/movements/", methods=["GET"])
@token_required
def get_transactions():
    filters = _get_transaction_input()
    limit = request.args.get("limit") or 10
    skip = request.args.get('skip') or 0
    transactions = repository.get_all(filters=filters, limit=limit, skip=skip)
    schema = TransactionSchema(many=True)
    serialized_transactions = schema.dump(transactions)
    return jsonify({"status": "success", "data": serialized_transactions}), 200


@app.route("/transaction/", methods=["POST"])
@token_required
def create_transaction():
    data = request.json
    schema = TransactionSchema()
    validated_data = schema.load(data)
    validated_data["linked_transaction_id"] = str(uuid4())
    transaction = service.repository.create(data=validated_data)
    return jsonify({"status": "success", "data": schema.dump(transaction)}), 200


@app.route("/transaction/execute/", methods=["GET"])
@token_required
def execute_transaction():
    if auth_service.is_admin():
        return jsonify({"status": "success", "data": execute_transactions()}), 200
    return jsonify({"status": "failure", "message": "Unauthorized"}), 403


@app.route("/transaction/rate/", methods=["POST"])
@token_required
def calculate_rate():
    data = request.json
    rate = api_rate_service.get_rate(
        origin_currency_name=data["origin_currency_name"],
        destination_currency_name=data["destination_currency_name"]
    )
    return jsonify({"status": "success", "data": {"rate": rate}}), 200
