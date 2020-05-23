from config import Config
import requests
import random
import string
import time
from random import randint

start_time = time.time()

def random_string(stringLength=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

BASE_URL = "http://localhost:5000/api/"
ENDPOINT_REGISTER = "register"
ENDPOINT_LOGIN = "login"
ENDPOINT_POSTS = "posts"
ENDPOINT_LIKE = "like"
headers={
    "User-Agent" : "Python/testscript",
    "Accept" : "*/*",
    "Content-Type": "application/json",
            }

users = []
posts = []

def register_users():
    url = BASE_URL + ENDPOINT_REGISTER
    i = 1
    while True:
        login = random_string()
        password = random_string()
        response = requests.post(
            url,
            headers = headers,
            json={
                "login":login,
                "password": password
            }
        )
        if response.status_code == 201:
            user = {"login":login, "password": password}
            users.append(user)
            i += 1
        if i >= Config().NUMBER_OF_USERS:
            break

def login_users():
    url = BASE_URL + ENDPOINT_LOGIN
    for user in users:
        response = requests.post(
            url,
            headers = headers,
            json={
                "login": user["login"],
                "password": user["password"]
            }
        ) 
        if response.status_code == 200: 
            user["token"] = response.json()["access_token"]

def make_posts():
    url = BASE_URL + ENDPOINT_POSTS
    for user in users:
        headers.update({"Authorization": "Bearer {}".format(user["token"])})
        i = 1
        while True:
            response = requests.post(
                url,
                headers = headers,
                json = {
                    "text": random_string(randint(1, 255))
                }
            )
            if response.status_code == 201: 
                posts.append(response.json()["post"]["id"])
                i += 1
            if i >= Config().MAX_POST_PER_USER:
                break

def make_likes():
    url = BASE_URL + ENDPOINT_POSTS + "/{}/" + ENDPOINT_LIKE
    for user in users:
        headers.update({"Authorization": "Bearer {}".format(user["token"])})
        i = 1
        while True:
            response = requests.post(
                url.format(random.choice(posts)),
                headers = headers
            )
            if response.status_code == 201:
                i += 1
            if i >= Config().MAX_LIKES_PER_USER:
                break

register_users()
login_users()
make_posts()
make_likes()
print("Execution time is {} s.".format((time.time() - start_time)))