import hashlib
import json
import redis


client = redis.StrictRedis(host='localhost', port=6379, db=0)
print("Flushing any old redis contents...")
client.flushall()
print("Done")


with open("terms.txt", "r") as fd:
    cnt = 0
    for line in fd:
        key, content = line.split("&&", 1)
        content = content.strip()
        cnt += 1
        if cnt % 100000 == 0:
            print("CNT: %s" % cnt)
        try:
            #result = client.setnx(key, content)
            result = client.zadd("gnd-autocomplete", 0, line)
            if not result:
                print("PROBLEM")
                print(cnt, key, content)
                print("--------")

        except:
            print("EXCEPT")
            print(cnt, key)
            print("++++++")

print client.zcard('gnd-autocomplete')
print(client.zcount('gnd-autocomplete', 0, 1))
