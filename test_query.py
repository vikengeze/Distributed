from time import time 
import requests
from random import randint

with open('query.txt') as file :
    lines = file.readlines()
keys = [key.strip().replace('/','_') for key in lines]
times =[]

# Change master_ip to match yours
master_ip = '192.168.0.1'
url = "http://{}:5000/overlay".format(master_ip)

response = requests.get(url)
addresses = response.text.split('\n')

responses = []
global_time_start = time()
for key in keys:
    t_start = time()
    node_getting_query = addresses[randint(0,9)] #SOS SOS SOS to 3 prepei na ginei arithmos twn komvwn pou trexoume kathe fora
    url = "http://{}/query/{}".format(node_getting_query,key)
    response = requests.get(url)
    # answer = response.text+' returned ,{} was asked and {} answered'.format(node_getting_query,response.url.split('//')[1].split('/')[0]) if response.text != 'Key not found!'  else response.text
    responses.append(response.text)
    t = time()
    times.append(t-t_start)
time_ = (time()-global_time_start)
for x in responses :
    print(x)
print('Read Throughput is: ',time_/len(keys))
print('\nTotal time required for executing all the requests: ',time_)