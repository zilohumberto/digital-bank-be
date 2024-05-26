from app import app
from flask import request, jsonify, g

from application.models import Account, AccountStatus
from application.repositories.persistence.entity_repository import EntityRepository
from application.services.account_service import AccountService
from application.validation_schemas import AccountSchema
from application.authentication import token_required
from application.tasks.account_tasks import validate_accounts_created
from application.services.auth_service import AuthService


repository = EntityRepository(model=Account)
service = AccountService(repository=repository)
auth = AuthService()


@app.route("/account/", methods=["GET"])
@token_required
def get_accounts():
    user_id = request.args.get('user_id')
    alias = request.args.get('alias')
    limit = request.args.get("limit") or 10
    skip = request.args.get('skip') or 0
    status = request.args.get('status') or None
    currency_name = request.args.get('currency_name') or None
    filters = {}
    if user_id:
        filters["user_id"] = user_id
    if alias:
        filters["alias"] = alias
    if currency_name:
        filters["currency_name"] = currency_name
    if status:
        filters["status"] = AccountStatus[status.upper()]
    accounts = repository.get_all(filters=filters, limit=limit, skip=skip)
    account_schema = AccountSchema(many=True)
    serialized_accounts = account_schema.dump(accounts)
    return jsonify({"status": "success", "data": serialized_accounts}), 200


@app.route("/account/", methods=["POST"])
@token_required
def create_account():
    data = request.json
    account_schema = AccountSchema()
    validated_data = account_schema.load(data)
    account = repository.create(data=validated_data)
    validated_data["user_id"] = g.user_id
    return jsonify({"status": "success", "data": account_schema.dump(account)}), 200


@app.route("/account/<string:pk>", methods=["PATCH"])
@token_required
def update_account(pk: str):
    validated_data = {}
    if "status" in request.json:
        validated_data["status"] = AccountStatus[request.json["status"].upper()]
        validated_data["id"] = pk
        if auth.is_admin():
            user_object = service.repository.update(data=validated_data)
            account_schema = AccountSchema()
            return jsonify({"status": "success", "data": account_schema.dump(user_object)}), 200
        return jsonify({"status": "failure", "message": "Unauthorized"}), 403
    return jsonify({"status": "failure", "message": "can be update only status for accounts"}), 404


@app.route("/account/validate/", methods=["GET"])
@token_required
def validate_accounts():
    if auth.is_admin():
        return jsonify({"status": "success", "data": validate_accounts_created()}), 200
    return jsonify({"status": "failure", "message": "Unauthorized"}), 403
