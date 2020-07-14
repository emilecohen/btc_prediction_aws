import json
import boto3
import requests
import pandas as pd
import time
import datetime
import os


BUCKET_NAME = 'sagemaker-us-east-2-535642252842'
s3 = boto3.client('s3')



def get_data(date):
    """ Query the API for 2000 days historical price data starting from "date". """
    
    url = "https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=2000&toTs={}&api_key=2f89100faea89908b275fc72a8543be88f0b977697e1919f74d47dd705f4e6dc".format(date)
    r = requests.get(url)
    ipdata = r.json()
    #df = pd.DataFrame(ipdata['Data'])
    return ipdata

def get_df(from_date, to_date):
    """ Get historical price data between two dates. """
    
    date = to_date
    holder = []
    # While the earliest date returned is later than the earliest date requested, keep on querying the API
    # and adding the results to a list. 
    while date > from_date:
        data = get_data(date)['Data']
        holder.append(pd.DataFrame(data['Data']))
        date = data['TimeFrom']
    # Join together all of the API queries in the list.    
    df = pd.concat(holder, axis = 0)                    
    # Remove data points from before from_date
    df = df[df['time']>from_date]                       
    # Convert to timestamp to readable date format
    df['time'] = pd.to_datetime(df['time'], unit='s')   
    # Make the DataFrame index the time
    df.set_index('time', inplace=True)                  
    # And sort it so its in time order 
    df.sort_index(ascending=True, inplace=True)      
    
    return df[['high', 'low', 'open', 'close']]
    
    
    
def request(start_date, df):
    
    timestamp = '00:00:00'
    
    # formatting start_date
    start_time = start_date +' '+ timestamp
    
    # formatting request_data
    request_data = {"instances": [{"start": start_time, "target": list(df.values)}],
                    "configuration": {"num_samples": 50,
                                      "output_types": ["quantiles"],
                                      "quantiles": ['0.1', '0.5', '0.9']}
                }
    
    json_input = json.dumps(request_data).encode('utf-8')
    print('Requesting prediction for '+start_time)
                
    return json_input
    
    
# helper function to decode JSON prediction
def decode_prediction(prediction, encoding='utf-8'):
    '''Accepts a JSON prediction and returns a list of prediction data.
    '''
    prediction_data = json.loads(prediction.decode(encoding))
    prediction_list = []
    for k in range(len(prediction_data['predictions'])):
        prediction_list.append(pd.DataFrame(data=prediction_data['predictions'][k]['quantiles']))
    return prediction_list


def upload_data_s3(result):
    
    # directories to save result data
    result_key = '/tmp/result.json'
    
    # write result JSON file
    with open(result_key, 'w') as f:
        json.dump(result, f) 

    result_s3=json.dumps(result, ensure_ascii=False)
    
    # uploading data to S3, and saving locations
    s3_response  = s3.put_object(Bucket=BUCKET_NAME, Key='deepar-btc-data/result/result.json', Body=result_s3)

    return s3_response




def lambda_handler(event, context):
    
    begin = "11/03/2013"
    end = datetime.datetime.today().strftime('%d/%m/%Y')
    
    from_date = time.mktime(datetime.datetime.strptime(begin, "%d/%m/%Y").timetuple())
    to_date = time.mktime(datetime.datetime.strptime(end, "%d/%m/%Y").timetuple())
    
    #Before calling the function, we test that our date interval is valid (ie difference is positive)
    # For that, we use datetime function
    assert (datetime.datetime.strptime(end, '%d/%m/%Y') - datetime.datetime.strptime(begin, '%d/%m/%Y')).days > 0
    
    df = get_df(from_date, to_date)
    
    # We test that the length of df is equal to the number of days between our 2 dates
    assert df.shape[0] == abs((datetime.datetime.strptime(end, '%d/%m/%Y') - datetime.datetime.strptime(begin, '%d/%m/%Y')).days + 1)
    
    open_df = df['open'].copy()
    
    
    # Creating the input data for the endpoint
    start_date_ = datetime.datetime.today() -  datetime.timedelta(days=1)
    start_date = start_date_.strftime('%Y-%m-%d')
    json_input = request(start_date, open_df)
    

    # The SageMaker runtime is what allows us to invoke the endpoint that we've created.
    runtime = boto3.Session().client('sagemaker-runtime')

    # Now we use the SageMaker runtime to invoke our endpoint, sending the review we were given
    response = runtime.invoke_endpoint(EndpointName = 'forecasting-deepar-2020-07-13-16-44-54-826',    # The name of the endpoint we created
                                       Body = json_input)                       # The actual data

    result_ = response['Body'].read()
    # The response is an HTTP response whose body contains the result of our inference
    
    result = json.loads(result_)

    # uploading results into s3
    data_dir = 'json_btc_data'
    upload_data_s3(result)

    return {
        'statusCode' : 200,
        'body' : result
    }

