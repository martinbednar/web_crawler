import json
import os
import argparse

import redis

class NoRedisURLException(Exception):
    pass

def parse_args():
    parser = argparse.ArgumentParser(description="Fills up the queue in redis with given name")
    parser.add_argument("--queue", help="name of the queue in redis", default="sites")
    parser.add_argument("--sites", "-s", help="path to JSON file containing information about sites to be crawled, required attributes are \"site\" and \"links\"", type=str, required=True)
    return parser.parse_args()

def get_redis():
    redis_url = os.environ.get('REDIS_URL')
    if not redis_url:
        raise NoRedisURLException

    return redis.Redis.from_url(redis_url)

def main():
    args = parse_args()
    redis = get_redis()

    with open(args.sites) as f:
        data = json.load(f)
        sites = data["sites"]

    for i, site in enumerate(sites):
        redis.rpush(args.queue, json.dumps(site))

if __name__ == "__main__":
    main()
