from argparse import ArgumentParser
from dht import dht_master_consistency

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

  args = parser.parse_args()
  dht_master_consistency.app.config["SERVER_NAME"] = "{0}:{1}".format(args.iphost, args.port)
  dht_master_consistency.app.config['HOST'] = args.iphost
  dht_master_consistency.app.config['FLUSH'] = args.flush
  dht_master_consistency.app.config['kreplicas'] = args.kreplicas
  dht_master_consistency.app.config['consistency'] = args.consistency
  dht_master_consistency.app.run(host=args.iphost, port=args.port)