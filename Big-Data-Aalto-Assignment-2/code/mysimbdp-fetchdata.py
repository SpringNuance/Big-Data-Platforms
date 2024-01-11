import os, shutil, argparse, json, pandas

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--micro_batching', type=str, default='No', help='Set "Yes" for micro-batching when size ingestion constraint not satisfied or "No" for discarting.')
    return parser.parse_args()
args = parse_args()

with open('code/config_ingestion_constraints.json', 'r') as file:
    ingestion_constraints = json.load(file)

def find_extension(filename):
    return filename.split('.')[-1]

def find_client_id(batch_filename):
    client_id_start = batch_filename.find('--client')+2
    file_extension = find_extension(batch_filename)
    client_id_end = batch_filename.find('.'+file_extension, client_id_start)
    return batch_filename[client_id_start:client_id_end]

def check_ingestion_constraints(first_batch_filename, batches_filenames):
    client_id = find_client_id(first_batch_filename)
    file_extension = find_extension(first_batch_filename)
    OK_type = file_extension==ingestion_constraints[client_id]['file_type']
    OK_number = sum([client_id==find_client_id(batch_filename) for batch_filename in batches_filenames])<=ingestion_constraints[client_id]['max_files_number']
    OK_size = os.path.getsize('code/client-input-directory/'+first_batch_filename)<=ingestion_constraints[client_id]['max_file_size']
    return OK_type, OK_number, OK_size

def microbatching(first_batch_filename):
    client_id = find_client_id(first_batch_filename)
    file_extension = find_extension(first_batch_filename)
    file_size = os.path.getsize('code/client-input-directory/'+first_batch_filename)
    max_file_size = ingestion_constraints[client_id]['max_file_size']
    number_microbatches = file_size//max_file_size+1
    if file_extension=='csv':
        batch = pandas.read_csv('code/client-input-directory/'+first_batch_filename)
    if file_extension=='json':
        batch = pandas.read_json('code/client-input-directory/'+first_batch_filename)
    for i in range(number_microbatches):
        microbatch = batch.iloc[int(batch.shape[0]*i/number_microbatches):int(batch.shape[0]*(i+1)/number_microbatches),:]
        microbatch_filename = 'code/client-stage-directory/'+first_batch_filename.replace('.'+file_extension,'')+'--microbatch'+str(i+1)+'.'+file_extension
        if file_extension=='csv':
            microbatch.to_csv(microbatch_filename)
        elif file_extension=='json':
            microbatch.to_json(microbatch_filename)
    os.remove('code/client-input-directory/'+first_batch_filename)

while True:
    batches_filenames = os.listdir('code/client-input-directory')
    if len(batches_filenames)>0:
        first_batch_filename = batches_filenames[0]
        OK_type, OK_number, OK_size = check_ingestion_constraints(first_batch_filename, batches_filenames)
        if OK_type and OK_number and OK_size:
            shutil.move('code/client-input-directory/'+first_batch_filename, 'code/client-stage-directory/'+first_batch_filename)
        elif OK_type and OK_number and not OK_size and args.micro_batching=='Yes':
            microbatching(first_batch_filename)
        else:
            os.remove('code/client-input-directory/'+first_batch_filename)