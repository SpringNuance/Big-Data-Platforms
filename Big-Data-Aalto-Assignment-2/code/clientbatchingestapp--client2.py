def ingestion(batch_path, client_id='client2'):

    import pymongo, time, os, bson, pandas

    mongo_client = pymongo.MongoClient('mongodb+srv://alvarorgaz:XLao4jEcoIz3kFXH@big-data-a1-j25ko.gcp.mongodb.net/admin?retryWrites=true&w=majority')
    database = mongo_client['google_play_store']
    table = database[client_id]
    
    batch = pandas.read_json(batch_path)
    start = time.time()
    request = table.insert(batch.to_dict(orient='records'))
    end = time.time()

    collection_stats = database.command("collstats", client_id)

    report = {
        'ingestion_size_local':os.path.getsize(batch_path),
        'ingestion_time':end-start,
        'successful_rows':len(request),
        'successful_rows_rate':len(request)/batch.shape[0],
        'collection_size':collection_stats['size'],
        'collection_count':collection_stats['count'],
        'collection_avgObjSize':collection_stats['avgObjSize']
    }

    del batch, start, end, request, collection_stats, table, database, mongo_client, client_id

    return report