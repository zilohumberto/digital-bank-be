from app import app
from flask import request, jsonify, g

from application.models import User, UserStatus
from application.repositories.persistence.entity_repository import EntityRepository
from application.services.user_service import UserService
from application.validation_schemas import UserSchema, LoginSchema, UserUpdateSchema
from application.services.auth_service import AuthService
from application.authentication import token_required
from application.tasks.user_tasks import validate_users_created


repository = EntityRepository(model=User)
service = UserService(repository=repository)
auth_service = AuthService()
user_schema = UserSchema()


@app.route("/login/", methods=["POST"])
def login():
    data = request.json
    validated_data = LoginSchema().load(data)
    user_object = service.repository.get(key=validated_data["email"], field="email")
    if user_object is None or user_object.is_deleted == True or user_object.status.value not in {"created", "active"}:
        # allow login even if the user is not active
        return jsonify({"status": "failure", "message": "User blocked or deleted"}), 404

    is_authenticated, token = auth_service.check_password(user=user_object, input_password=validated_data["password"])
    if is_authenticated is False:
        return jsonify({"status": "failure", "message": "Unauthorized"}), 404

    response_data = user_schema.dump(user_object)
    response_data["token"] = token
    return jsonify({"status": "success", "data": response_data}), 200



@app.route("/user/", methods=["POST"])
def create_user():
    data = request.json
    validated_data = user_schema.load(data)
    # encrypt password on DB!
    validated_data["password"] = auth_service.key_producer.make_password(validated_data["password"])
    user_object = service.create_user(validated_data)
    return jsonify({"status": "success", "data": user_schema.dump(user_object)}), 201


@app.route("/user/<string:pk>", methods=["GET"])
@app.route("/user/", methods=["GET"])
@token_required
def get_user(pk: str = None):
    if pk is None:
        limit = request.args.get("limit") or 10
        skip = request.args.get('skip') or 0
        is_deleted = request.args.get('is_deleted') or None
        status = request.args.get('status') or None
        email = request.args.get('email') or None
        filters = {}
        if is_deleted is not None:
            filters["is_deleted"] = is_deleted
        if status is not None:
            filters["status"] = UserStatus[status.upper()]
        if email is not None:
            filters["email"] = email
        user_schema = UserSchema(many=True)
        user_object = service.repository.get_all(filters=filters, limit=limit, skip=skip)
    else:
        user_schema = UserSchema()
        user_object = service.repository.get(key=pk)

    return jsonify({"status": "success", "data": user_schema.dump(user_object) }), 200


@app.route("/user/<string:pk>", methods=["PATCH"])
@token_required
def update_user(pk: str):
    data = request.json
    validated_data = UserUpdateSchema().load(data)
    if not auth_service.is_admin():
        if "status" in validated_data:
            # only admins are allowed to update the status of a user!
            del validated_data["status"]
    validated_data["id"] = pk
    user_object = service.repository.update(data=validated_data)
    return jsonify({"status": "success", "data": user_schema.dump(user_object)}), 200


@app.route("/user/<string:pk>", methods=["DELETE"])
@token_required
def delete_user(pk: str):
    service.repository.update(data={"id": pk, "status": UserStatus.INACTIVE})
    service.repository.delete(pk=pk)
    return jsonify({"status": "success", "data":"ok"}), 204



@app.route("/user/validate/", methods=["GET"])
@token_required
def validate_users():
    if auth_service.is_admin():
        return jsonify({"status": "success", "data": validate_users_created()}), 200
    return jsonify({"status": "failure", "message": "Unauthorized"}), 403
