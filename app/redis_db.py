from redis import Redis
from os import getenv


redis_storage = Redis(host=getenv('redis_host'),
                      port=int(getenv('redis_port')),
                      db=int(getenv('redis_db')),
                      decode_responses=True)
