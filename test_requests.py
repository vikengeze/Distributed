from time import time 
import requests
from random import randint

with open('requests.txt') as file :
    lines = file.readlines()
reqs = [req.split(',')[0] for req in lines]
keys = [key.split(',')[1][1:].strip().replace('/','_') for key in lines]
values =list(map(lambda x:x.split(',')[-1].strip() if len(x.split(','))==3 else '',lines))

# Change master_ip to match yours
master_ip = '192.168.0.1'
url = "http://{}:5000/overlay".format(master_ip)

response = requests.get(url)
addresses = response.text.split('\n')

responses = []
query_times = []
insert_times = []
global_time_start = time()
errors = 0
dictionary_for_freshness_check = dict()
for req, key, value in zip(reqs,keys,values):
    if req == 'query':
        t_start = time()
        node_getting_query = addresses[randint(0,9)]#SOS SOS SOS to 9 prepei na ginei arithmos twn komvwn pou trexoume kathe fora
        url = "http://{}/query/{}".format(node_getting_query,key)
        response = requests.get(url)
        if response.text != 'Key not found!' :
            errors = errors+1 if response.text.split(',')[0].split('\'')[1] != dictionary_for_freshness_check[key] else errors
        
        responses.append(response.text)
        t = time()
        query_times.append(t-t_start)
    else :
        dictionary_for_freshness_check[key]=value
        t_start = time()
        url = "http://{}/insert/{}".format(addresses[randint(0,9)],key)
        payload= value
        headers = {
        'Content-Type': 'text/plain'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        t = time()
        insert_times.append(t-t_start)
global_time_stop = time()
tmp = [val for val in values if val!='']
tmp_ = [empty for empty in values if empty=='']
for response in responses:
    print(response)
print('The number of not so fresh returned from queries are:', errors)
print('Write Throughput is: ',(global_time_stop-global_time_start)/len(tmp))
print('Read Throughput is ',(global_time_stop-global_time_start)/len(tmp_))
print('\nTotal time required for executing all the requests: ',global_time_stop-global_time_start)