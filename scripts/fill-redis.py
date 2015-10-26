# Fill redis DB with autocomplete values.
#
import re
import redis

ENTRY_FORM = re.compile("(.+)\(([^\)\(]+)\)\&\&(.+)\n$")


client = redis.StrictRedis(host='localhost', port=6379, db=0)
print("Flushing any old redis contents...")
client.flushall()
print("Done")


with open("terms.txt", "r") as fd:
    cnt = 0
    for line in fd:
        match = ENTRY_FORM.match(line)
        if not match:
            continue
        normalized, key, content = match.groups()
        cnt += 1
        if cnt % 100000 == 0:
            print("CNT: %s" % cnt)
        try:
            result = client.zadd(
                "gnd-autocomplete", 0, "%s (%s)&&%s (%s)" % (
                    normalized, key, content, key))
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
