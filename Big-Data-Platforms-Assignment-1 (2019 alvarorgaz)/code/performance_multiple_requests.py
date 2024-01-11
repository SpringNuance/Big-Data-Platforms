import argparse, requests, time, threading, pymongo
import pandas as pd
import numpy as np

r = lambda x: round(x, 4)

class data_ingest_thread(threading.Thread):    
	
	def __init__(self, args):
		threading.Thread.__init__(self)
		self.n_requests = args.n_requests_by_thread
		self.ingestion_mode = args.ingestion_mode
		if self.ingestion_mode=='daas':
			self.server_address = args.server_address
	
	def run(self):
		times = []
		if self.ingestion_mode=='no_daas':
			mongo_client = pymongo.MongoClient('mongodb+srv://alvarorgaz:XLao4jEcoIz3kFXH@big-data-a1-j25ko.gcp.mongodb.net/admin?retryWrites=true&w=majority')
			database = mongo_client['google_play_store']
			table = database['apps']
		start_thread = time.time()
		for i in range(self.n_requests):
			row_to_ingest = data.sample()
			row_to_ingest_json = row_to_ingest.to_dict(orient='records')
			id = row_to_ingest.index[0]
			app = row_to_ingest.App[id]	
			start = time.time()
			if self.ingestion_mode=='daas':
				request = requests.post(self.server_address+'ingestion', json=row_to_ingest_json)
				times.append(time.time()-start)
				print('Request status ', request.reason, 'for app:', ascii(app), '(row '+str(id)+') in', r(times[-1]), 'seconds')
			elif self.ingestion_mode=='no_daas': 
				table.insert(row_to_ingest_json)
				times.append(time.time()-start)
				print('Ingested app:', ascii(app), '(row '+str(id)+') in ', r(times[-1]), 'seconds')
		print('Thread ends in ', r(time.time()-start_thread), 'seconds with requests times: mean', r(np.mean(times)), 'std', r(np.std(times)), 'min', r(np.min(times)), 'max', r(np.max(times)))	

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--n_threads', type=int, default=1, help='Number of concurrent threads to test.')
	parser.add_argument('--n_requests_by_thread', type=int, default=1, help='Total number of sampled data rows to be ingested.')
	parser.add_argument('--ingestion_mode', type=str, default='daas', help='Set as "daas" to use REST API and as "no_dass" to use API of MongoDB')
	parser.add_argument('--server_address', type=str, default='http://35.228.191.152/')
	return parser.parse_args()
args = parse_args()

data = pd.read_csv('./data/googleplaystore.csv')
args.server_address = args.server_address+'apps/'
for _ in range(args.n_threads):
	thread = data_ingest_thread(args)
	thread.start()