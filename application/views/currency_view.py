from app import app
from flask import request, jsonify

from application.models import Currency
from application.repositories.persistence.entity_repository import EntityRepository
from application.validation_schemas import CurrencySchema
from application.authentication import token_required

repository = EntityRepository(model=Currency)


@app.route("/currency/", methods=["GET"])
@token_required
def get():
    name = request.args.get('name')
    limit = request.args.get("limit") or 10
    skip = request.args.get('skip') or 0
    if name is None:
        currencies = repository.get_all(filters={}, limit=limit, skip=skip)
    else:
        currencies = repository.get(key=name, field="name")

    schema = CurrencySchema(many=True)
    serialized_data = schema.dump(currencies)
    return jsonify({"status": "success", "data": serialized_data}), 200


@app.route("/currency/", methods=["POST"])
@token_required
def create():
    data = request.json
    schema = CurrencySchema()
    validated_data = schema.load(data)
    currency = repository.create(data=validated_data)
    return jsonify({"status": "success", "data": schema.dump(currency)}), 200
