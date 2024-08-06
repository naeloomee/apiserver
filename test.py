from flask import Flask, jsonify, request, abort
from pymongo import MongoClient
#from pymongo.errors import ConnectionError
from bson.objectid import ObjectId

app = Flask(__name__)

# MongoDB 연결 설정
client = MongoClient('mongodb://172.20.224.1:27017/')
db = client['db_test']
collection = db['coll_test']

# MongoDB 연결 확인
@app.route('/health', methods=['GET'])
def health_check():
    try:
        client.admin.command('ping')
        return jsonify({'status': 'healthy'}), 200
    except ConnectionError:
        return jsonify({'status': 'unhealthy'}), 500

# CREATE: 새로운 항목 추가
@app.route('/items', methods=['POST'])
def create_item():
    if not request.json or 'name' not in request.json or 'medal' not in request.json:
        abort(400)
    item = {
        'name': request.json['name'],
        'medal': request.json['medal']
    }
    result = collection.insert_one(item)
    return jsonify({'_id': str(result.inserted_id)}), 201

# READ: 모든 항목 조회
@app.route('/items', methods=['GET'])
def get_items():
    items = list(collection.find())
    for item in items:
        item['_id'] = str(item['_id'])  # ObjectId를 문자열로 변환
    return jsonify(items), 200

# READ: 특정 항목 조회
@app.route('/items/<item_id>', methods=['GET'])
def get_item(item_id):
    try:
        item = collection.find_one({'_id': ObjectId(item_id)})
    except Exception:
        abort(400)
    if item is None:
        abort(404)
    item['_id'] = str(item['_id'])  # ObjectId를 문자열로 변환
    return jsonify(item), 200

# UPDATE: 특정 항목 수정
@app.route('/items/<item_id>', methods=['PUT'])
def update_item(item_id):
    if not request.json:
        abort(400)
    update_fields = {}
    if 'name' in request.json:
        update_fields['name'] = request.json['name']
    if 'medal' in request.json:
        update_fields['medal'] = request.json['medal']
    
    try:
        result = collection.update_one({'_id': ObjectId(item_id)}, {'$set': update_fields})
    except Exception:
        abort(400)
    if result.matched_count == 0:
        abort(404)
    return jsonify({'status': 'updated'}), 200

# DELETE: 특정 항목 삭제
@app.route('/items/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    try:
        result = collection.delete_one({'_id': ObjectId(item_id)})
    except Exception:
        abort(400)
    if result.deleted_count == 0:
        abort(404)
    return jsonify({'status': 'deleted'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
