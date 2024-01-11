import pandas as pd
import requests, argparse

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--n_requests', type=int, default=1, help='Total number of sampled data rows to be ingested via daas.')
	parser.add_argument('--ingest_all', type=str, default='No', help='Set as "Yes" to ingest all data rows without random sampling.')
	parser.add_argument('--server_address', type=str, default='http://35.228.191.152/')
	parser.add_argument('--dataset', type=str, default='apps', help='Set as "apps" or "reviews" to ingest data from desired file.')
	return parser.parse_args()
args = parse_args()

if args.dataset=='apps':
	data = pd.read_csv('./data/googleplaystore.csv')
	server_address = args.server_address+'apps/'
elif args.dataset=='reviews':
	data = pd.read_csv('./data/googleplaystore_user_reviews.csv')
	server_address = args.server_address+'reviews/'
	
if args.ingest_all=='Yes':
	for i in data.index:
		row_to_ingest = data.loc[[i],:]
		row_to_ingest_json = row_to_ingest.to_dict(orient='records')
		request = requests.post(server_address+'ingestion', json=row_to_ingest_json)
		print('Request status:', request.reason)
else:
	for i in range(args.n_requests):
		row_to_ingest = data.sample()
		row_to_ingest_json = row_to_ingest.to_dict(orient='records')
		request = requests.post(server_address+'ingestion', json=row_to_ingest_json)
		print('Request status:', request.reason)
	print(args.server_address+'ingestion')