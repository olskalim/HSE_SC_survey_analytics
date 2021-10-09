import csv
import requests
import vk
from private_data import VK_personal_token

def get_polls(owner_id):
    ID = []
    k = 0
    url = f"https://api.vk.com/method/wall.get?owner_id={owner_id}&access_token={VK_personal_token}&v=5.131"
    req = requests.get(url, params={'owner_id': owner_id,'count': 100, 'offset': k})
    src = req.json()
    mx = src["response"]["count"]
    while k < mx:
        req = requests.get(url, params={'owner_id': owner_id, 'offset': k})
        src = req.json()
        posts = src["response"]["items"]
        for post in posts:
            if "attachments" in post:
                for x in post["attachments"]:
                    if "poll" in x:
                        ID.append(x["poll"]["id"])
            k += 1
    return ID  # [id, ...]

def get_poll_results(poll_id):
    poll_data = api.polls.getById(poll_id=poll_id)
    variants = [x['id'] for x in poll_data['answers']]
    variants_with_names = [(x['id'], x['text']) for x in poll_data['answers']]
    votes = api.polls.getVoters(poll_id=poll_id, answer_ids=variants)
    users_by_variants = {}
    for k in range(len(variants_with_names)):
        users_by_variants[variants_with_names[k]] = votes[k]['users']['items']
    return users_by_variants  # {(variant_id, variant_name): [voters], ...}


def get_names(ids):
    # max number of requested users - 1000
    names = sorted([(x['last_name'], x['first_name'], x['id'])
                    for x in api.users.get(user_ids=ids)])
    return names  # [(last_name, first_name, id), ...]


def write_to_csv(names, results, answers, path="output.csv"):
    ids = [x[2] for x in names]
    with open(path, "w", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(['']+[x[0]+" "+x[1] for x in names])
        for i, k in enumerate(answers):
            row = [k[1]]
            row += [1 if x in results[i] else 0 for x in ids]
            writer.writerow(row)



def main():
    # poll_id = "637266255"
    group_id = "-206802048" 
    polls = get_polls(group_id)
    for poll_id in polls:
        results = list(get_poll_results(poll_id).values())
        answers = list(get_poll_results(poll_id))
        voters_ids = set()
        for i in range(len(results)):
            for x in results[i]:
                voters_ids.add(x)
        voters = sorted(get_names(list(voters_ids)))
        write_to_csv(voters, results, answers, f"data/poll-{poll_id}.csv")

if __name__ == "__main__":
    session = vk.Session(access_token=VK_personal_token)
    api = vk.API(session, v='5.131', lang='ru')
    main()

# script output in output.txt
