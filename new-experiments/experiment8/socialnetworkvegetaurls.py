import time
import random
import os
import json

# Initialize random seed
random.seed(int(time.time() * 1000))
random.random(); random.random(); random.random()

charset = list('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890')
decset = list('1234567890')

# url = "http://c220g2-030832.wisc.cloudlab.us:31565"
url = "http://c220g2-010604.wisc.cloudlab.us:32291"
# Load env vars
max_user_index = int(os.getenv("max_user_index", 962))

def string_random(length):
    return ''.join(random.choice(charset) for _ in range(length))

def dec_random(length):
    return ''.join(random.choice(decset) for _ in range(length))

def compose_post(filename:str, print_file = None):
    user_index = random.randint(0, max_user_index - 1)
    username = f"username_{user_index}"
    user_id = str(user_index)
    text = string_random(256)
    num_user_mentions = random.randint(0, 5)
    num_urls = random.randint(0, 5)
    num_media = random.randint(0, 4)
    media_ids = []
    media_types = []

    for _ in range(num_user_mentions):
        while True:
            user_mention_id = random.randint(0, max_user_index - 1)
            if user_index != user_mention_id:
                break
        text += f" @username_{user_mention_id}"

    for _ in range(num_urls):
        text += f" http://{string_random(64)}"

    for _ in range(num_media):
        media_id = dec_random(18)
        media_ids.append(media_id)
        media_types.append("png")

    method = "POST"
    path = f"{url}/wrk2-api/post/compose"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    # body = {
    #     "username": username,
    #     "user_id": user_id,
    #     "text": text
    # }

    body = f"username={username}&user_id={user_id}&text={text}"
    
    if num_media:
        # body["media_ids"] = media_ids
        # body["media_types"] = media_types
        body += f"&media_ids={media_ids}&media_types={media_types}"
    
    # body["post_type"] = media_types
    body += "&post_type=0"
    
    # with open(filename, "w") as f:
    #     f.write(body)
        # json.dump(body,f)

    print(file=print_file)
    print(f"{method} {path}",file=print_file)
    print("Content-Type: application/x-www-form-urlencoded",file=print_file)
    print(f"@{filename}",file=print_file)

    # return method, path, headers, body

def read_user_timeline(print_file = None):
    user_id = str(random.randint(0, max_user_index - 1))
    start = str(random.randint(0, 100))
    stop = str(int(start) + 10)

    args = f"user_id={user_id}&start={start}&stop={stop}"
    method = "GET"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    path = f"{url}/wrk2-api/user-timeline/read?{args}"
    # print(path)
    print(f"{method} {path}",file=print_file)
    return method, path, headers, None

def read_home_timeline(print_file = None):
    user_id = str(random.randint(0, max_user_index - 1))
    start = str(random.randint(0, 100))
    stop = str(int(start) + 10)

    args = f"user_id={user_id}&start={start}&stop={stop}"
    method = "GET"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    path = f"{url}/wrk2-api/home-timeline/read?{args}"
    # print(path)
    print(f"{method} {path}", file=print_file)

def request(print_file = None):
    read_home_timeline_ratio = 0.5
    read_user_timeline_ratio = 0.5
    # compose_post_ratio = 0.10

    coin = random.random()
    if coin < read_home_timeline_ratio:
        read_home_timeline(print_file)
    elif coin < read_home_timeline_ratio + read_user_timeline_ratio:
        read_user_timeline(print_file)
    # else:
    #     compose_post()

# Initialize random seed
os.makedirs("vegeta_compose_body", exist_ok=True)
print_file_names = [f"vegeta_socialnetwork_m{i+1}.txt" for i in range(10)]
random.seed(int(time.time() * 1000))
compose_num = 0
with open("vegeta_socialnetwork_gp.txt","w") as print_file:
    for i in range(60*15*10000):
        coin = random.random()
        if coin <= 0.9:
            request(print_file)
        else:
            compose_post(f"vegeta_compose_body/data_{compose_num}.txt", print_file)

            # with open(f"vegeta_compose_body/data_{compose_num}.txt", 'r') as f:
            #     content = f.read()

            # content = content.replace("'", '"')

            # with open(f'vegeta_compose_body/data_{compose_num}.txt', 'w') as f:
            #     f.write(content)
            compose_num += 1

# for print_file_name in print_file_names:
#     with open(print_file_name,"w") as print_file:
#         for i in range(60*15*900):
#             coin = random.random()
#             if coin <= 0.9:
#                 request(print_file)
#             else:
#                 compose_post(f"vegeta_compose_body/data_{compose_num}.txt", print_file)

                # with open(f"vegeta_compose_body/data_{compose_num}.txt", 'r') as f:
                #     content = f.read()

                # content = content.replace("'", '"')

                # with open(f'vegeta_compose_body/data_{compose_num}.txt', 'w') as f:
                #     f.write(content)
                # compose_num += 1


        

# os.makedirs("vegeta_compose_body", exist_ok=True)
# os.makedirs("vegeta_compose_body", exist_ok=True)
# for i in range(1000):
#     compose_post(f"vegeta_compose_body/data_{i}.txt")
#     with open("vegeta_compose_body/data_{i}.txt", 'r') as f:
#         content = f.read()

#     content = content.replace("'", '"')

#     with open(f'h2load_compose_body/data_{i}.txt', 'w') as f:
#         f.write(content)