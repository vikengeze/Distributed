from flask import Flask, redirect, url_for, request, logging, abort, render_template
import os
import time
import threading
import requests
from dht.dht_consistency import DHTNode

app = Flask(__name__, static_folder="../visualize/dist", static_url_path="")

m = 160 #TODO: prepei na ginei 160
node = None

@app.before_first_request
def startup(): 
  global node,k,consistency
  k = app.config['kreplicas']
  consistency = app.config['consistency']
  addr = app.config['SERVER_NAME']
  print(k,consistency, end='\n')
  my_dict = {}  
  node = DHTNode(addr, m, my_dict)
  if app.config['FLUSH']:
    node.my_dict.clear()
  print("This server's id is {0}".format(node.id))

@app.route('/join_request', methods=['GET'])
def joinreq():
  host = request.args.get('host')
  port = request.args.get('port')
  time.sleep(0.5)
  url = "http://{0}:{1}/".format(host, port)
  #print(url)
  requests.get(url)
  return ''
  
#Endpoint to begin the startup process
@app.route('/', methods=['GET'])
def ping():
  print("This server is ready")
  return ''

#Every node that comes alive, joins through the master:
@app.route('/dht/join', methods=['POST', 'PUT'])
def join():
  addr = request.args.get('data')
  print("Node joining is {0}".format(addr))
  try:
    node.join(addr)
    return "ok", 200
  except ConnectionError:
    return abort(404)

#End point to find a successor for a new node entering
@app.route('/dht/find_successor', methods=['GET'])
def find_successor():
  id = int(request.args.get('id'))
  return _find_successor(node, id)

#helper function to find the successor
def _find_successor(node, id):
  #get the successor of current node
  succ = node.get_successor()
  #if the hash is between node and its successor, return its successor as the node "in charge"
  if DHTNode.between(id, node.id, node.get_hash(succ)):
    return succ
  #else, search again for the key, using node's successor as current node.
  url =  "http://{0}/dht/find_successor?id={1}".format(succ, id)
  r = requests.get(url)
  return r.text

#Helper endpoint for slave's depart - updates copies of other nodes
@app.route('/update_depart',methods=['POST'])
def update_depart():
  i = int(request.args.get('i'))
  key = int(request.args.get('key'))
  val = request.args.get('val')
  ok = node.update_depart(int(key), str(val), int(i), k)
  if not ok:
      abort(404)
  return "Done updating copies of departing node"


#Set node's Key = key, Value = [replica,value]
@app.route('/set_key', methods=['POST', 'PUT'])
def set_key():
  key = request.args.get('key')
  val = request.args.get('val')
  node.set_key(key,eval(val))
  return "ok", 200

#Inserting a key, starting from this node. GET http://{SLAVE_URL}/db/key , Body->raw->Value
@app.route('/insert/<key>', methods=['POST', 'PUT'])
def insert(key):
  #find key's hash
  h = node.get_hash(key)
  #find key's successor, starting from current node
  succ = _find_successor(node, h)
  #if the successor is the current node:
  if succ == node.host:
    print("I am the one who should have the key! ")
    value=request.data
    node.set_key(key, (1, value))
    # start_node = node.host
    succ = node.get_successor()
    print("I inserted the first replica of {0}".format(str(node.get_key(key))))
    #task to be executed in the background for eventual - right away for linear
    def long_running_task(succ, key, value):
      url = "http://{0}/inserting?key={1}&val={2}&i={3}".format(succ, key, value, 2)
      r = requests.post(url)
      if r.status_code==200:
        print("Now I'm done with the other {0} replicas".format(k))
    #starting thread for eventual consistency / no thread for linear consistency:
    #EVENTUAL CONSISTENCY:
    if(consistency == "eventual"):
      thread = threading.Thread(target=long_running_task, args = (succ, key, value,))
      thread.start()
    #LINEAR CONSISTENCY:
    elif(consistency == "linear"):
      long_running_task(succ, key, value)
    #shows when the 1st copy is done:
    print("I completed the insert request") 
    return "ok", 200
  #if the successor is another node, send the request to your successor
  if succ != node.host:
    succ=node.get_successor()
    url = "http://" + succ + url_for('insert', key=key)
    r = requests.post(url, data = request.data)
    if r.status_code == 200:
      return "ok", 200
    return abort(404)

@app.route('/inserting', methods=['POST', 'PUT'])
def inserting():
    key = request.args.get('key')
    value = request.args.get('val')
    i = int(request.args.get('i'))
    if(int(i)<=k):
      url = "http://{0}/set_key?key={1}&val={2}".format(node.host, key,(i,value))
      r = requests.post(url)
      if r.status_code != 200:
        return "can't do"
      succ=node.get_successor()
      url = "http://{0}/inserting?key={1}&val={2}&i={3}".format(succ, key, value, i+1)
      r = requests.post(url)
      return ""
    return ""
    

#helper function to query the key
def searching(node,key,asking_node):
  val = node.get_key(key)
  print ("searching in {} for key, while {} asked for it".format(node.host,asking_node))
  #if the value is in this node
  if val:
    #LINEAR CONSISTENCY:
    if (consistency=='linear'):
      print(consistency)
      #check if this is the last replica. In linear consistency, we want to get data from the last.
      if(int(val[0]) == k):
        print("I had the desired replica of the key {0}!".format(key))
        return(node.host)
      else:
        return ""
    #EVENTUAL CONSISTENCY:
    if (consistency=='eventual'):
      print("I had the desired replica of the key {0}!".format(key))
      return(node.host)
  h = node.get_hash(key)
  #if the key belongs in this node, return null because we didn't find it
  if DHTNode.between(h, node.get_hash(node.get_predecessor()), node.id):
    return None
  return ""

#search for a certain key
@app.route('/query/<key>', methods=['GET'])
def query(key):
  if(key=='*'):
    #start from current node
    start=node.host
    #empty list for key-value pairs
    pairs = []
    #search for current node's keys:
    url = "http://{0}/keys".format(start)
    r = requests.get(url)
    print("I got {0} from {1}".format(r.text,node.host))
    #add current node's pairs to the list
    pairs.append(r.text)
    #get current node's successor
    succ = node.get_successor()
    curr = node.host
    while succ != curr and succ != start:
      #find the successor's keys
      url = "http://{0}/keys".format(succ)
      r = requests.get(url)
      print("I got {0} from {1}".format(r.text,succ))
      #add them to the list
      pairs.append(r.text)
      url = "http://{0}/get_successor".format(succ)
      r = requests.get(url)
      if r.status_code == 200:
        curr = succ
        #get the next successor
        succ = r.text
      else:
        abort(404)
    return "\n".join(pairs)
  #now if we want just one specific key
  asking_node=node.host
  #based on consistency, search for the value in current node:
  node_responsible = searching(node, key, asking_node)
  #if current node has the desired replica:
  if(node_responsible == node.host):
    val = node.get_key(key)
    value = " Value: {0} (Replica {1})".format(str(val[1])[1:],val[0])
    return("{}, '{}' had it and answered".format(value,node.host))
  #else, pass the query to the successor
  succ = node.get_successor()
  url = "http://{0}/give_key/{1}/{2}".format(succ, key, node.host)
  r = requests.get(url)
  if r.status_code == 200:
    node_responsible = r.text
  else:
    abort(404)
  #if the key was supposed to be there but isn't, it doesnt exist.
  if(node_responsible == ""):
    return ("Key not found!")
  #Get the response from the node who has the desired replica
  url = "http://{}/get_response/{}".format(node_responsible,key)
  r = requests.get(url)
  return ("{} and {} answered!".format(r.text,node.host))


#helper endpoint to return the key to the node that asked for it.
@app.route('/give_key/<key>/<asking_node>', methods=['GET'])
def give(key, asking_node):
  #send same get request to the successor
  node_responsible = searching(node, key, asking_node)
  #if the key was supposed to be there but isn't, it doesnt exist.
  if(node_responsible == None):
    return ""
  #if we found node_responsible, return it
  if(node_responsible !=""):
    return node_responsible
  succ = node.get_successor()
  url = "http://{0}/give_key/{1}/{2}".format(succ, key, asking_node)
  r = requests.get(url)
  if r.status_code != 200:
    abort(404)
  else:
    return r.text

@app.route('/get_response/<key>', methods=['GET'])
def responded(key):
  val = node.get_key(key)
  value = " Value: {0} (Replica {1})".format(str(val[1])[1:],val[0])
  return("{}, '{}' had it".format(value,node.host))


#Endpoint to return all keys stored in one node
@app.route('/keys', methods=['GET'])
def keys():
  pairs = []
  for s in node.my_dict.keys():
    val= node.my_dict.get(s)
    pairs.append("Key Hash: {0}, Value: {1} (Replica {2})".format(s, str(val[1])[1:], val[0]))
  return "\n".join(pairs)

#hash, inserts a new hash-value pair to a certain node's dictionary (or updates existing value)
#This is for tranfering keys
@app.route('/db/hash/<hash>', methods=['POST', 'PUT'])
def put_hash(hash):
  node.my_dict[str(hash)] = eval(request.data)
  return "ok", 200

#Delete key
@app.route('/delete/<key>', methods=['DELETE'])
def delete(key):
  val = node.get_key(key)
  h = node.get_hash(key)
  #find the successor of the key
  succ = _find_successor(node, h)
  #if the key should be in this node but val is empty, the key doesnt exist.
  if succ == node.host and val=='':
    return "The key does not exist! We are really sorry about that :'(", 200
  if succ == node.host:
    val = node.get_key(key)
    if val:
      node.delete_key(key)
      succ=node.get_successor()
      #task to be executed in the background for eventual - right away for linear
      def long_deleting_task(k, succ, key):
        url = "http://{0}/delete_replicas/{1}/{2}".format(succ, key, 2)
        res = requests.delete(url)
        if res.status_code != 200:
          return abort(404)
      print("Now I'm done deleting the {0} replicas".format(k))
      #starting thread for eventual consistency / no thread for linear consistency:
      #EVENTUAL CONSISTENCY:
      if(consistency == "eventual"):
        thread = threading.Thread(target=long_deleting_task, args = (k, succ, key,))
        thread.start()
      #LINEAR CONSISTENCY:
      elif(consistency == "linear"):
        long_deleting_task(k, succ, key )
      #shows when the 1st copy is done:
      print("I'm done with delete request")
      return "deleted", 200
    else:
      return "Key not found!"
  else:
    succ= node.get_successor()
    url="http://{}/delete/{}".format(succ,key)
    res = requests.delete(url)
    if res.status_code != 200:
      return abort(404)
    return res.text

#Delete key
@app.route('/delete_replicas/<key>/<i>', methods=['DELETE'])
def delete_replicas(key,i):
  val = node.get_key(key)
  i = int(i)
  if val:
    node.delete_key(key)
    if(i<k):
      succ=node.get_successor()
      url = "http://{0}/delete_replicas/{1}/{2}".format(succ, key, i+1)
      res = requests.delete(url)
      if res.status_code != 200:
        return abort(404)
    return "deleted", 200
  return "There were no replicas here"

# transfering keys when needed
@app.route('/db/transfer', methods=['POST'])
def transfer():
  addr = request.args.get('addr')
  #list of the keys of the successor
  keys = [s for s in node.my_dict.keys()]
  #list for the replicas of the successor the new node is going to take:
  old_keys=[]
  #list for the new keys of the successor the new node is going to take:
  new_keys=[]
  for key in keys:
    #if the key doesn't belong between new node and succ, it belongs to the new node:
    if not DHTNode.between(int(key), node.get_hash(addr), node.id):
      print("I'm giving this key: {0} to {1}".format(key,addr))
      new_keys.append(key)
      ok = node.transfer(int(key), addr, k)
      if not ok:
        abort(404)
    else:
      old_keys.append(key)
      print("Now I'm gving replicas of {0} to {1}, -> {0}".format(key,addr))
      ok=node.transfer_copies(int(key), addr, k)
      if not ok:
        abort(404)
  succ = node.host
  for key in old_keys:
    url = "http://{0}/update_copies?i={1}&key={2}".format(succ,1,key)
    r = requests.post(url)
  succ = node.get_successor()
  for key in old_keys:
    url = "http://{0}/update_copies?i={1}&key={2}&iteration={3}".format(succ,2,key,2)
    r = requests.post(url)
  for key in new_keys:
    url = "http://{0}/update_copies?i={1}&key={2}&iteration={3}".format(succ,1,key,2) #isws i+1
    r = requests.post(url)
  return "updated", 200

#updating copies during join of a new node
@app.route('/update_copies',methods=['POST'])
def update_copies():
  i = int(request.args.get('i'))
  key = int(request.args.get('key'))
  iteration = int(request.args.get('iteration'))
  ok = node.update_copies(int(key), int(i), k)
  if not ok:
    abort(404)
  if(iteration<k):
    succ = node.get_successor()
    url = "http://{0}/update_copies?i={1}&key={2}&iteration={3}".format(succ,i+1,key,iteration+1)
    r = requests.post(url)
  return "updated_copies"

#Get node's successor
@app.route('/get_successor', methods=['GET'])
def get_successor():
  return node.get_successor()

#Get node's predecessor
@app.route('/get_predecessor', methods=['GET'])
def get_predecessor():
  return node.get_predecessor()

#Set node's successor
@app.route('/set_successor', methods=['POST', 'PUT'])
def set_successor():
  addr = request.args.get('addr')
  node.update_successor(addr)
  return "ok", 200

#Set node's predecessor
@app.route('/set_predecessor', methods=['POST', 'PUT'])
def set_predecessor():
  addr = request.args.get('addr')
  node.update_predecessor(addr)
  return "ok", 200

#Starting from current node, print all nodes in chord
@app.route('/overlay', methods =['GET'])
def overlay():
  peers = []
  peers.append(node.host)
  succ = node.get_successor()
  curr = node.host
  while succ != curr and succ != peers[0]:
    peers.append(succ)
    url = "http://{0}/get_successor".format(succ)
    r = requests.get(url)
    if r.status_code == 200:
      curr = succ
      succ = r.text
    else:
      abort(404)
  return "\n".join(peers)