from flask import Flask, jsonify, request
from datetime import datetime
import uuid
from myapp import app

users_data = {}
categories_data = {}
records_data = {}

@app.route("/")
def welcome_page():
    return f"<p>Welcome to the experimental API!</p><a href='/healthcheck'>Healthcheck</a>"

@app.route("/healthcheck")
def health_check():
    response = jsonify(timestamp=datetime.now(), status="OK")
    response.status_code = 200
    return response

@app.route("/user/<int:user_id>", methods=['GET', 'DELETE'])
def manage_user():
    if request.method == 'GET':
        user_info = users_data.get(user_id)
        if not user_info:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user_info)
    elif request.method == 'DELETE':
        deleted_user = users_data.pop(user_id, None)
        if not deleted_user:
            return jsonify({"error": "User not found"}), 404
        return jsonify(deleted_user)

@app.route('/user', methods=['POST'])
def create_new_user():
    user_data = request.get_json()
    if "username" not in user_data:
        return jsonify({"error": "Username is required"}), 400
    user_id = uuid.uuid4().hex
    new_user = {"id": user_id, **user_data}
    users_data[user_id] = new_user
    return jsonify(new_user)

@app.route('/users', methods=['GET'])
def get_all_users():
    return jsonify(list(users_data.values()))

@app.route('/category', methods=['POST', 'GET', 'DELETE'])
def manage_category():
    if request.method == 'POST':
        category_data = request.get_json()
        if "name" not in category_data:
            return jsonify({"error": "Name is required"}), 400
        category_id = uuid.uuid4().hex
        new_category = {"id": category_id, **category_data}
        categories_data[category_id] = new_category
        return jsonify(new_category)
    elif request.method == 'GET':
        return jsonify(list(categories_data.values()))
    elif request.method == 'DELETE':
        category_id_to_delete = request.args.get('id')
        if category_id_to_delete:
            deleted_category = categories_data.pop(category_id_to_delete, None)
            if not deleted_category:
                return jsonify({"error": f"Category with id {category_id_to_delete} not found"}), 404
            return jsonify(deleted_category)
        else:
            categories_data.clear()
            return jsonify({"message": "All categories have been deleted"})

@app.route('/record/<int:record_id>', methods=['GET', 'DELETE'])
def manage_record():
    if request.method == 'GET':
        record_info = records_data.get(record_id)
        if not record_info:
            return jsonify({"error": "Record not found"}), 404
        return jsonify(record_info)
    elif request.method == 'DELETE':
        deleted_record = records_data.pop(record_id, None)
        if not deleted_record:
            return jsonify({"error": "Record not found"}), 404
        return jsonify(deleted_record)

@app.route('/record', methods=['POST', 'GET'])
def create_or_get_records():
    if request.method == 'POST':
        record_data = request.get_json()
        user_id = record_data.get('user_id')
        category_id = record_data.get('category_id')

        if not user_id or not category_id:
            return jsonify({"error": "Both user_id and category_id are required"}), 400
        if user_id not in users_data:
            return jsonify({"error": f"User with id {user_id} not found"}), 404
        if category_id not in categories_data:
            return jsonify({"error": f"Category with id {category_id} not found"}), 404

        new_record_id = uuid.uuid4().hex
        new_record = {"id": new_record_id, **record_data}
        records_data[new_record_id] = new_record
        return jsonify(new_record)
    elif request.method == 'GET':
        user_id_to_filter = request.args.get('user_id')
        category_id_to_filter = request.args.get('category_id')
        if not user_id_to_filter and not category_id_to_filter:
            return jsonify({"error": "Specify user_id or category_id"}), 400
        filtered_records = [
            r for r in records_data.values() if (not user_id_to_filter or r['user_id'] == user_id_to_filter) or (not category_id_to_filter or r['category_id'] == category_id_to_filter)
        ]
        return jsonify(filtered_records)
