from time import time 
import requests
from random import randint

with open('insert.txt') as file :
    lines = file.readlines()
keys = [x.split(',')[0].replace('/','_') for x in lines]
values = [x.split(',')[-1].split('\n')[0][1:] for x in lines]

# Change master_ip to match yours
master_ip = '192.168.0.1'
url = "http://{}:5000/overlay".format(master_ip)

response = requests.get(url)
addresses = response.text.split('\n')

times =[]
global_time_start = time()
for value,key in zip(values,keys):
    t_start = time()
    url = "http://{}/insert/{}".format(addresses[randint(0,9)],key)
    payload= value
    headers = {
    'Content-Type': 'text/plain'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    t = time()
    times.append(t-t_start)
    end_time = time()
print('Write Throughput is: ',(end_time -global_time_start)/len(keys))
print('\nTotal time required for executing all the requests: ',time()-global_time_start)