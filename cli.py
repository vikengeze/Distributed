import random 
import requests
import re

responses = 'on'
master = 'off'

while(True):
	mode = input("Please select operating method(random/node): ")
	if (mode == 'random' or mode == 'node'):
		break
	else:
		print("Invalid input, select 'random' for random query targets or 'node' to execute queries on a specific node")

if (mode == 'random'):
	url = 'http://192.168.68.110:5000/overlay'
	response = requests.get(url)
	node_list = response.text.splitlines()
elif (mode == 'node'):
	while(True):
		node = input("Please input node information(format x.x.x.x:port):") 
		if (re.match('[0-9]+.[0-9]+.[0-9]+.[0-9]+:[0-9]+', node)):
			print('Selecting node on address ' + node.split(':')[0] + ', listening on port ' + node.split(':')[1])
			if (node.split(':')[1] == '5000'):
				print("Identified master(bootstrap) node")
				master='on'
			break
		else:
			print('Invalid input')
else:
	print("Unexpected error")

print("Welcome to ToyChord, a simple file sharing application! Please type help for more information :)")

while(True):
	
	if (mode == 'random'):
		master='off'
		node = random.choice(node_list)
		print("Executing on node " + str(node))
		if (node.split(':')[1] == '5000'):
			master = 'on'
			print("Identified master(bootstrap) node")

	read = input("Waiting for input: ")
	
	if (re.match('insert, [A-Za-z0-9\'\.()? ]+, [A-Za-z0-9]+', read)):
		key = read.split(', ')[1]
		key = key.replace(' ', '_')
		value = read.split(', ')[2]
		url = 'http://' + node + '/insert/' + key
		response = requests.post(url, data=value)
		if (responses == 'on'):
			print(response.text)
	elif (re.match('delete, [A-Za-z\'\.()? ]+', read)):
		key = read.split(', ')[1]
		key = key.replace(' ', '_')
		url = 'http://' + node + '/delete/' + key
		response = requests.delete(url)
		if (responses == 'on'):
			print(response.text)
	elif (re.match('query, [A-Za-z\'\.()?* ]+', read)):
		key = read.split(', ')[1]
		key = key.replace(' ', '_')
		url = 'http://' + node + '/query/' + key 
		response = requests.get(url)
		if (responses == 'on'):
			print(response.text)
	elif (read == 'depart'):	
		if (master == 'on'):
			print('Master cannot depart from DHT')
		else:
			url = 'http://' + node + '/depart'
			response = requests.get(url)
			if (responses == 'on'):
				print(response.text)
			if (mode == 'node'):
				print("Exiting CLI...")
				exit()
			else:
				node_list.remove(node)
	elif (read == 'overlay'):
		url = 'http://' + node + '/overlay'
		response = requests.get(url)
		if (responses == 'on'):
			print(response.text)
	elif (read == 'node_change' and mode == 'node'):
		while(True):
			node = input("Please input node information(format x.x.x.x:port):") 
			if (re.match('[0-9]+.[0-9]+.[0-9]+.[0-9]+:[0-9]+', node)):
				print('Selecting node on address ' + node.split(':')[0] + ', listening on port ' + node.split(':')[1])
				if (node.split(':')[1] == '5000'):
					print("Identified master(bootstrap) node")
					master='on'
				break
			else:
				print('Invalid input')
	elif (read == 'node_change' and mode == 'node'):
		print("Not supported when on random mode")
	elif (read == 'help'):
		print(" ----------------------------------------------------------")
		print("| insert, key, value: inserts new key, value pair          |")
		print("|        delete, key: deletes key, value entry             |")
		print("|         query, key: returns value of entry key           |")
		print("|             depart: node departs from system             |")
		print("|            overlay: prints DHT topology                  |")
		print("|               help: provides this information            |")
		print("|               exit: exit CLI                             |")
		print("|        node_change: change target node(node mode only)   |")
		print(' ----------------------------------------------------------')
	elif (read == 'exit'):
		break
	else:
		print("Invalid input, please type help for more information")

