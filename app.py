from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import post_dump
from flask_msearch import Search

from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['DEBUG'] = True

db = SQLAlchemy(app)
ma = Marshmallow(app)


class Address(db.Model):
    __searchable__ = ['line1', 'line2', 'city', 'state', 'zip']

    id = db.Column(db.Integer, primary_key=True)
    line1 = db.Column(db.String(30))
    line2 = db.Column(db.String(30), nullable=True)
    city = db.Column(db.String(15))
    state = db.Column(db.String(4))
    zip = db.Column(db.String(10))
    date_created = db.Column(db.DateTime, default=datetime.now)


class AddressSchema(ma.Schema):
    SKIP_VALUES = set([None])
   
    class Meta:
        fields = ('line1', 'line2', 'city', 'state', 'zip')

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value not in self.SKIP_VALUES
        }


search = Search(db=db)
search.init_app(app)

addresses_schema = AddressSchema(many=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/addresses', methods=['POST'])
def all_addresses():
    req_data = request.get_json()

    for data in req_data:
        if 'line2' not in data:
            data['line2'] = None
        address = Address(line1=data['line1'],
                          line2=data['line2'],
                          city=data['city'],
                          state=data['state'],
                          zip=data['zip'])

        db.session.add(address)
        db.session.commit()

    return 'Success!', 200


@app.route('/search1/<string:contains>', methods=['GET'])
def search1(contains):
    search_results = Address.query.msearch(contains, limit=20)
    result = addresses_schema.dump(search_results)
    # print(result, result)
    
    return jsonify(result), 200


@app.route('/search2/', methods=['PUT'])
def search2():
    req_data = request.get_json()

    search_results = Address.query.msearch(req_data["address"], limit=20)
    result = addresses_schema.dump(search_results)
        
    return jsonify(result), 200


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)