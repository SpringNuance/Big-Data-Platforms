import pymongo, jsons
from flask import Flask, request
from flask_restplus import Resource, Api

mongo_client = pymongo.MongoClient('mongodb+srv://alvarorgaz:XLao4jEcoIz3kFXH@big-data-a1-j25ko.gcp.mongodb.net/admin?retryWrites=true&w=majority')
database = mongo_client['google_play_store']
table_apps = database['apps']
table_reviews = database['reviews']

flaskapp = Flask(__name__)
app = Api(app=flaskapp)
app_apps = app.namespace('apps', description='API concerning applications data.')
app_reviews = app.namespace('reviews', description='APIs concerning reviews data.')

@app_apps.route('/ingestion', methods=['POST'])
class ingestion(Resource):
    def post(self):
        table_apps.insert(request.json)
        return ''

@app_reviews.route('/ingestion', methods=['POST'])
class ingestion(Resource):
    def post(self):
        table_reviews.insert(request.json)
        return ''

@app_apps.route('/filter/<app_name>')
class filter(Resource):
    def get(self, app_name):
        table_apps.create_index([('App', 'text')])
        output = list(table_apps.find({'$text': {'$search': app_name}}))
        return jsons.dumps(output)
    def post(self, app_name):
        table_apps.create_index([('App', 'text')])
        output = list(table_apps.find({'$text': {'$search': app_name}}))
        return jsons.dumps(output)

@app_reviews.route('/filter/<app_name>')
class filter(Resource):
    def get(self, app_name):
        table_reviews.create_index([('App', 'text')])
        output = list(table_reviews.find({'$text': {'$search': app_name}}))
        return jsons.dumps(output)
    def post(self, app_name):
        table_reviews.create_index([('App', 'text')])
        output = list(table_reviews.find({'$text': {'$search': app_name}}))
        return jsons.dumps(output)
		
flaskapp.run(host='0.0.0.0', port=80)