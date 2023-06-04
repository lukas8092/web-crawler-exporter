import re

pattern = r"https?:\/\/(?:www.)?([\w\d-]+\.[\w]+)((?:\/[\w\d-]+)*)"

res = re.search(pattern,"https://www.spsejecna.cz/score/student")

print(bool(res))
print(res.groups())