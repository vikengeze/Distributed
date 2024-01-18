from hashlib import sha1
from threading import Thread, Lock
import requests
import sys
import time
from flask.json import JSONEncoder, JSONDecoder
class DHTNode(object):
    def __init__(self, host, m, my_dict):
        self.host = host
        self.m = m
        self.id = self.get_hash(self.host)
        self.predecessor = self.host
        self.pred_lock = Lock()
        self.successor = self.host
        self.succ_lock = Lock()
        self.my_dict = my_dict

    def join(self, addr):
        h = self.get_hash(addr)
        succ = self._find_successor(h)
        url =  "http://{0}/get_predecessor".format(succ)
        pred = requests.get(url).text
        url =  "http://{0}/set_successor?addr={1}".format(addr, succ)
        requests.post(url)
        url =  "http://{0}/set_successor?addr={1}".format(pred, addr)
        requests.post(url)
        url =  "http://{0}/set_predecessor?addr={1}".format(succ, addr)
        requests.post(url)
        url =  "http://{0}/set_predecessor?addr={1}".format(addr, pred)
        requests.post(url)
        url =  "http://{0}/db/transfer?addr={1}".format(succ, addr)
        requests.post(url)

        

    def depart(self, k):
        succ = self.get_successor()
        pred = self.get_predecessor()
        try:
            url = "http://" + pred + '/set_successor?addr=' + succ
            res = requests.post(url)
            if res.status_code != 200:
                return False
            url = "http://" + succ + '/set_predecessor?addr=' + pred
            res = requests.post(url)
            if res.status_code != 200:
                return False
        except Exception:
            print()
            return False
        return True

    def transfer(self, hash, addr, k):
        if addr == self.host:
            return True
        data = self.my_dict.get(str(hash))
        url = "http://" + addr + '/db/hash/' + str(hash)
        res = requests.post(url, data=(str(data)))
        if res.status_code != 200:
            return False
        #make data a tuple
        data = eval(str.encode(str(data)))
        print("Transfering data {1} from {0} to {2}".format(self.host,data,addr))
        #update the node's replica of the key. if we have more than 1 replicas, now it will be (2,value)
        if int(data[0]) < k:
            new_value = int(data[0])+1
            new_data = (new_value, data[1])
            self.my_dict[str(hash)]= new_data
        else:
            self.my_dict.pop(str(hash))
        return True

    def transfer_copies(self, hash, addr, k):
        if addr == self.host:
            return True
        data = self.my_dict.get(str(hash))
        data = eval(str.encode(str(data)))
        if int(data[0]) > 1:
            url = "http://" + addr + '/db/hash/' + str(hash)
            res = requests.post(url, data=(str(data)))
            if res.status_code != 200:
                return False
        return True

    def update_copies(self, hash, i, k):
        data = self.my_dict.get(str(hash))
        if data:
            data = eval(str.encode(str(data)))
            print("This is data I'm trying to update: {0}. i is {1} and k is {2}".format(data, i, k))
            if int(data[0]) < k and int(data[0]) > i:
                new_value = int(data[0]) + 1
                new_data=(new_value, data[1])
                self.my_dict[str(hash)]= new_data
            #if the current replica was the kth, it's now taken and needs to be removed.
            elif int(data[0]) == k and int(data[0]) > i:
                print("I'm removing {0}, cause I had the last replica and it's now taken from pred".format(data))
                self.my_dict.pop(str(hash))
        return True

    #used to update keys of successors and nodes after them when a node departs
    def update_depart(self, hash, val, i, k):
        data = eval(val)
        if data:
            new_value = int(data[0]) + i
            # print("this is new value {0}".format(new_value))
            if new_value <= k :
                new_data=(new_value, data[1])
                # print("this is new data {0}".format(new_data))
                url = "http://" + self.host + '/db/hash/' + str(hash)
                # print("this is url {0}".format(url))
                res = requests.post(url, data=(str(new_data)))
                if res.status_code != 200:
                    return False
        return True

    def update_successor(self, succ):
        self.succ_lock.acquire()
        self.successor = succ
        self.succ_lock.release()

    #return my successor
    def get_successor(self):
        self.succ_lock.acquire()
        succ = self.successor
        self.succ_lock.release()
        return succ
    
    #return my predecessor
    def get_predecessor(self):
        self.pred_lock.acquire()
        pred = self.predecessor
        self.pred_lock.release()
        return pred
    
    def update_predecessor(self, pred):
        self.pred_lock.acquire()
        self.predecessor = pred
        self.pred_lock.release()
   
    def get_key(self, key):
        #get the hash value of the key
        h = str(self.get_hash(key))
        #get the value from the dictionary, using hash
        value = self.my_dict.get(h)
        if value is not None:
            return value
        return ""

    def set_key(self, key, value):
        #get hash value of the key
        h = self.get_hash(key)
        #insert hash value of key in the dictionary, along with key value
        self.my_dict[str(h)]= value
    
    def delete_key(self, key):
        h = self.get_hash(key)
        self.my_dict.pop(str(h))

    @staticmethod
    def between(x, a, b):
        if a > b:
            return a < x or b >= x
        elif a < b:
            return a < x and b >= x
        else:
            return a !=x

    def get_hash(self, key):
        return int(int.from_bytes(sha1(key.encode()).digest(), byteorder='big'))
        # return int(sha1(key.encode()).hexdigest())
    def _find_successor(self, id):
        succ = self.get_successor()
        if DHTNode.between(id, self.id, self.get_hash(succ)):
            return succ
        url =  "http://{0}/dht/find_successor?id={1}".format(succ, id)
        r = requests.get(url)
        return r.text

    def _find_predecessor(self):
        pred = self.get_predecessor()
        return pred
