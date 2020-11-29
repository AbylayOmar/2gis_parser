from json import load
import csv

with open("cafe/cafes.json", "r") as f:
    data = load(f)

f = csv.writer(open('test.csv','w+'))
f.writerow(['address_name', 'full_name', 'name', 'contact_groups', 'external_content'])

for id in data:
    nd = data[id]['data']['entity']['profile'][id]['data']
    try:
        f.writerow([nd['address_name'], nd['full_name'], nd['name'], nd['contact_groups'], nd['external_content']])
    except:
        continue