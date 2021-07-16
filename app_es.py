from datetime import datetime
from flask import Flask, jsonify, request
from elasticsearch import Elasticsearch

es = Elasticsearch()

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    results = es.get(index='addresses', doc_type='title', id='94132')
    return jsonify(results['_source'])


@app.route('/insert_data', methods=['POST'])
def insert_data():
    req_data = request.get_json()

    addresses = []
    for data in req_data:

        if 'line2' not in data:
            data['line2'] = None

        line1 = data['line1'],
        line2 = data['line2'],
        city = data['city'],
        state = data['state'],
        zip = data['zip']

        body = {
            'line1': line1,
            'line2': line2,
            'city': city,
            'state': state,
            'zip': zip,
            'timestamp': datetime.now()
        }

        addresses.append(es.index(index='addresses', body=body))

    return jsonify(addresses)


@app.route('/search', methods=['POST'])
def search():
    keyword = request.get_json()['keyword']

    body = {
        "query": {
            "multi_match": {
                "query": keyword
            }
        }
    }

    res = es.search(index="addresses", body=body)

    addresses = []
    for hit in res['hits']['hits']:
        addresses.append(hit['_source'])

    return jsonify(addresses)
    return jsonify(res['hits']['hits'])

app.run(port=5000, debug=True)