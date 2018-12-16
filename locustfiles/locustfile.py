from locust import HttpLocust, TaskSet
import json
from decouple import config, Csv

def login(l):
    data = {
        "email": config('EMAIL'),
        "password": config('PASSWORD')
    }
    l.client.post("/api/v1/login/", data=json.dumps(data))

def get_flights(l):
    l.client.get("/api/v1/flight/")

class UserBehavior(TaskSet):
    tasks = {get_flights: 2, login: 2}

    def on_start(self):
        self.client.headers['Content-Type'] = "application/json"
        self.client.headers['Authorization'] = "Bearer {}".format(config('TOKEN'))

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000