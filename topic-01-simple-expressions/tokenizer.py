import re

p = re.compile("ab*")

if p.match("abbbbbbb") :
    print("match")
else:
    print("not match")