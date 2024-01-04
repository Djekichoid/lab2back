from flask import Flask, jsonify, request, abort
from datetime import datetime
from myapp import app, db
from myapp.scemas import UserSchema, CategorySchema, RecordSchema, IncomeAccountSchema
from myapp.models import User, Category, Record, IncomeAccount
from marshmallow.exceptions import ValidationError
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, verify_jwt_in_request, get_jwt_identity
from passlib.hash import pbkdf2_sha256

jwt = JWTManager(app)

with app.app_context():
    db.create_all()
    db.session.commit()

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return (
        jsonify({"message": "The token has expired.", "error": "token_expired"}),
        401,
    )

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return (
        jsonify(
            {"message": "Signature verification failed.", "error": "invalid_token"}
        ),
        401,
    )

@jwt.unauthorized_loader
def missing_token_callback(error):
    return (
        jsonify(
            {
                "description": "Request does not contain an access token.",
                "error": "authorization_required",
            }
        ),
        401,
    )

@app.route("/")
def home():
    return f"<p>Home Page!</p><a href='/healthcheck'>Health Status</a>"

@app.route("/healthcheck")
def health_check():
    response = jsonify(date=datetime.now(), status="OK")
    response.status_code = 200
    return response

@app.route('/user/<int:user_id>', methods=['GET', 'DELETE'])
@jwt_required()
def manage_user(user_id):
    with app.app_context():
        jwt_claims = verify_jwt_in_request()

        if jwt_claims is None:
            return jsonify({'error': 'Invalid token'}), 400

        current_user_id = get_jwt_identity()

        user = User.query.get(user_id)

        if current_user_id != user_id:
            return jsonify({'error': 'Permission denied'}), 403

        if not user:
            return jsonify({'error': f'User {user_id} does not exist'}), 404

        income_account = IncomeAccount.query.filter_by(user_id=user_id).first()

        if request.method == "GET":
            user_data = {
                'id': user.id,
                'username': user.username,
                'income_balance': income_account.balance if income_account else 0.0
            }
            return jsonify(user_data), 200

        elif request.method == "DELETE":
            try:
                db.session.delete(user)
                if income_account:
                    db.session.delete(income_account)
                db.session.commit()
                return jsonify({'message': f'User {user_id} deleted'}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500

@app.route('/user/register', methods=['POST'])
def create_user():
    data = request.get_json()

    user_schema = UserSchema()

    try:
        user_data = user_schema.load(data)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400

    new_user = User(
        username=user_data["username"],
        password=pbkdf2_sha256.hash(user_data["password"]),
        income_account=IncomeAccount(**user_data.get("income_account", {}))
    )

    with app.app_context():
        db.session.add(new_user)
        db.session.commit()

        user_response = {
            'user_id': new_user.id,
            'income_balance': new_user.income_account.balance
        }

        return jsonify(user_response), 200

@app.route('/user/login', methods=['POST'])
def login_user():
    data = request.get_json()

    user_schema = UserSchema()

    try:
        user_data = user_schema.load(data)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400

    username = user_data["username"]
    provided_user_id = user_data["id"]

    with app.app_context():
        user = User.query.filter_by(id=provided_user_id, username=username).first()

        if user:
            is_valid_credentials = pbkdf2_sha256.verify(user_data["password"], user.password)

            if provided_user_id is not None and is_valid_credentials:
                access_token = create_access_token(identity=user.id)
                return jsonify({"message": "Successful login", "token": access_token, "user_id": user.id}), 200
            else:
                return jsonify({"message": "Unsuccessful login (invalid credentials)"}), 401
        else:
            return jsonify({"message": "Unsuccessful login (user not found)"}), 404

@app.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    with app.app_context():
        users_data = {
            user.id: {"username": user.username} for user in User.query.all()
        }
        return jsonify(users_data)

@app.route('/category', methods=['POST', 'GET'])
@jwt_required()
def manage_category():
    if request.method == 'GET':
        with app.app_context():
            categories_data = {
                category.id: {"name": category.name} for category in Category.query.all()
            }
            return jsonify(categories_data)

    elif request.method == 'POST':
        data = request.get_json()
        cat_schema = CategorySchema()

        try:
            cat_data = cat_schema.load(data)
        except ValidationError as err:
            return jsonify({'error': err.messages}), 400

        new_category = Category(name=cat_data["name"])

        with app.app_context():
            db.session.add(new_category)
            db.session.commit()

            category_response = {
                "id": new_category.id,
                "name": new_category.name
            }

            return jsonify(category_response), 200

@app.route('/category/<int:cat_id>', methods=['DELETE'])
@jwt_required()
def delete_category(cat_id):
    with app.app_context():
        category = Category.query.get(cat_id)

        if not category:
            return jsonify({'error': f'Category {cat_id} not found'}), 404

        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': f'Category {cat_id} deleted'}), 200

@app.route('/records', methods=['GET'])
@jwt_required()
def get_all_records():
    with app.app_context():
        records_data = {
            "records": [
                {
                    "id": record.id,
                    "user_id": record.user_id,
                    "category_id": record.category_id,
                    "amount": record.amount,
                    "created_at": record.created_at
                } for record in Record.query.all()
            ]
        }
        return jsonify(records_data)

@app.route('/record/<int:record_id>', methods=['GET', 'DELETE'])
@jwt_required()
def manage_record(record_id):
    with app.app_context():
        record = Record.query.get(record_id)

        if not record:
            return jsonify({"error": f"Record {record_id} not found"}), 404

        if request.method == "GET":
            record_data = {
                "id": record.id,
                "user_id": record.user_id,
                "category_id": record.category_id,
                "amount": record.amount,
                "created_at": record.created_at
            }
            return jsonify(record_data), 200

        elif request.method == "DELETE":
            db.session.delete(record)
            db.session.commit()
            return jsonify({'message': f'Record {record_id} deleted'}), 200

@app.route('/record', methods=['POST', 'GET'])
@jwt_required()
def manage_records():
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        category_id = request.args.get('category_id')

        if not user_id and not category_id:
            return jsonify({'error': 'Specify user_id or category_id'}), 400

        query = Record.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        if category_id:
            query = query.filter_by(category_id=category_id)

        need_records = query.all()
        records_data = {
            record.id: {
                "user_id": record.user_id,
                "category_id": record.category_id,
                "amount": record.amount,
                "created_at": record.created_at
            } for record in need_records
        }
        return jsonify(records_data)

    elif request.method == 'POST':
        data = request.get_json()

        record_schema = RecordSchema()

        try:
            record_data = record_schema.load(data)
        except ValidationError as err:
            return jsonify({'error': err.messages}), 400

        user_id = record_data['user_id']
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if user.income_account.balance < record_data['amount']:
            return jsonify({'error': 'Insufficient funds'}), 400

        user.income_account.balance -= record_data['amount']
        db.session.commit()

        new_record = Record(
            user_id=user_id,
            category_id=record_data['category_id'],
            amount=record_data['amount']
        )

        with app.app_context():
            db.session.add(new_record)
            db.session.commit()

            record_response = {
                "id": new_record.id,
                "user_id": new_record.user_id,
                "category_id": new_record.category_id,
                "amount": new_record.amount
            }

            return jsonify(record_response), 200
