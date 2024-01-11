import pymongo, argparse
import pandas as pd

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--dataset', type=str, default='apps', help='Set as "apps" or "reviews" to ingest data from desired file.')
	return parser.parse_args()
args = parse_args()

mongo_client = pymongo.MongoClient('mongodb+srv://alvarorgaz:XLao4jEcoIz3kFXH@big-data-a1-j25ko.gcp.mongodb.net/admin?retryWrites=true&w=majority')
database = mongo_client['google_play_store']
table = database['apps']

if args.dataset=='apps':
	data = pd.read_csv('./data/googleplaystore.csv')
elif args.dataset=='reviews':
	data = pd.read_csv('./data/googleplaystore_user_reviews.csv')

for i in data.index:
	row_to_ingest = data.loc[[i],:]
	row_to_ingest_json = row_to_ingest.to_dict(orient='records')		
	id = row_to_ingest.index[0]
	app = row_to_ingest.App[id]
	table.insert(row_to_ingest_json)
	print('Ingested app:', ascii(app), '(row '+str(id)+')')