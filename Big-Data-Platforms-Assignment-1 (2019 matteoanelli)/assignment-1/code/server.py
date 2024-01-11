from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import json
import os

from producer import producer

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'mysimbdp-coredms'
app.config['MONGO_URI'] = os.environ.get('MONGO_URL')

mongo = PyMongo(app)

@app.route('/document/<partid>', methods=['GET'])
def get_one(partid):
    documents = mongo.db.documents

    query = documents.find({'part_id': int(partid)})
    if not query:
        results = 'No results found'

    else:
        results = []
        for q in query:
            data = {
                'part_id': q['part_id'],
                'ts_date': q['ts_date'],
                'ts_time': q['ts_time'],
                'room': q['room']
            }
            results.append(data)
    return jsonify({'result': results})
#TODO check if empty

@app.route('/document',methods=['POST'])
def insert_one():
    part_id = request.json['part_id']
    ts_date = request.json['ts_date']
    ts_time = request.json['ts_time']
    room = request.json['room']

    new_record = {
                'part_id': int(part_id),
                'ts_date': int(ts_date),
                'ts_time': ts_time,
                'room': room
            }
    message = producer(json.dumps(new_record))

    return message


if __name__ == '__main__':
    app.run(debug=True)

