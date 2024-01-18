from argparse import ArgumentParser
from dht import dht_slave_consistency
import os
import requests
import signal

if __name__ == '__main__':
  parser = ArgumentParser(
    description='PiplineDHT -- A simple distributed hash table')
  parser.add_argument('-i', '--iphost', action='store', required=True,
                      help='hostname to bind to')
  parser.add_argument('-p', '--port', action='store', type=int,
                      required=True, help='port to bind to')
  parser.add_argument('-k', '--kreplicas', action='store', default=1,type=int,
                      help='number of replicas')
  parser.add_argument('-c', '--consistency', action='store', default='linear',
                      help='type of consistency')
  parser.add_argument('-f', '--flush', action='store_true',
                      default=False, help="Flush the db for testing")
  parser.add_argument('-mp', '--master', action='store',
                      required=False,default='192.168.0.1:5000', help="IP and port of master node")

  args = parser.parse_args()
  dht_slave_consistency.app.config["SERVER_NAME"] = "{0}:{1}".format(args.iphost, args.port)
  dht_slave_consistency.app.config['HOST'] = args.iphost
  dht_slave_consistency.app.config['FLUSH'] = args.flush
  dht_slave_consistency.app.config['master'] = args.master
  dht_slave_consistency.app.config['kreplicas'] = args.kreplicas
  dht_slave_consistency.app.config['consistency'] = args.consistency

  pid = os.fork()
  if pid > 0:
    dht_slave_consistency.app.run(host=args.iphost, port=args.port)
  else:
    requests.get("http://{0}/join_request?host={1}&port={2}".format(args.master, args.iphost, args.port)) 
    os.kill(os.getpid(), signal.SIGKILL)