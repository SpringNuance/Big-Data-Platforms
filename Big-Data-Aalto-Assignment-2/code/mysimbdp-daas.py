from flask import Flask, request
from flask_restplus import Resource, Api
from datetime import datetime

flaskapp = Flask(__name__)
app = Api(app=flaskapp)
app_batch = app.namespace('batch', description='APIs concerning full datasets to client-input-directory (batch ingestion).')

@app_batch.route('/ingestion', methods=['POST'])
class ingestion(Resource):
    def post(self):
        client_id = request.files['client_id'].read().decode("utf-8")
        file_extension = request.files['file'].filename.split('.')[-1]
        filename = 'code/client-input-directory/'+str(datetime.now()).replace(':', '-')+'--'+client_id+'.'+file_extension
        request.files['file'].save(filename)
        return ''

flaskapp.run(host='0.0.0.0', port=80)