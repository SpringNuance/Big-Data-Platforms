import requests, argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--client_id', type=str, help='Set the client ID.')
    parser.add_argument('--server_address', type=str, default='http://35.228.211.137/')
    parser.add_argument('--dataset_path', type=str, help='Set the path of the dataset to ingest including ".csv".')
    return parser.parse_args()
args = parse_args()

server_address = args.server_address+'batch/ingestion'
request = requests.post(server_address, files={'client_id':args.client_id,'file':open(args.dataset_path, 'r', encoding='utf-8')})
print('File submission request status:', request.reason)