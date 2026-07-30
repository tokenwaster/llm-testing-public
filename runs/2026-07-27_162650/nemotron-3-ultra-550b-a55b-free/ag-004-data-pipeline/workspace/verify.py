import json
data = json.load(open('output.json'))
print('Count:', len(data))
print('Keys:', [list(d.keys()) for d in data])
print('All scores int:', all(isinstance(d['score'], int) for d in data))
print('All dates YYYY-MM-DD:', all(len(d['signup'])==10 and d['signup'][4]=='-' and d['signup'][7]=='-' for d in data))
print('Emails:', [d['email'] for d in data])
print('Signups:', [d['signup'] for d in data])
print('Scores:', [d['score'] for d in data])