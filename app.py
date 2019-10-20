import pymongo
import redis
import json
from bson.json_util import dumps
import sys
import os

# mongodb databse connection
uri = 'mongodb://127.0.0.1:27017/'
myclient = pymongo.MongoClient(uri)
mydb = myclient["dummy"]

#redis connection
import redis
rds = redis.StrictRedis(port=6379, db=0)


#redis custom class to store and retrive api data
class Red:
    def set(cache_key, api):
        #dumps is to convert json data to string because redis accept string data
        api = json.dumps(api)
        # syntax to store response first param is key and second is value
        rds.set(cache_key, api)
        # here is the expire time for cache data you can change the time(in seconds)
        rds.expire(cache_key, 432000)

    def get(cache_key):
        #check the key if exist
        cacheData = rds.get(cache_key)
        if cacheData:
            # as we stored api response in string format 
            # we have to convert it into json data
            cacheData = cacheData.decode("utf-8")
            cacheData = cacheData.replace("'", "\"")
            cacheData = json.loads(cacheData)
            return cacheData
        else:
            # if key is not exist it will return None
            # so that we can again recheck our db for result
            return None


def get_data():
    # here i have added system argument to get key from user 
    # example: You can run "python app.py your_cache_key"
    # here your_cache_key will treat as the key in redis db for current result
    # if you are running python app.py it will take default_token as key

    try:
        cache_key = sys.argv[1]
    except IndexError:
        cache_key = "default_token"

    cacheData = Red.get(cache_key)
    # Here we are checking if the cachedata exist in redis db for current key
    # if exist it will return here immedietly instead of going down
    # if not exist it will go down

    if cacheData:
        return cacheData

    # here mysb is the redis db name and comment is the connection name of mongodb
    mycol  = mydb['comments']
    # here we are doing bit of calculaton by fetching data
    query = mycol.find({"postId" : {"$gt": 1}})
    post_ids = []
    for i in query:
        post_ids.append(i)

    group = {
        "$group" : {
                "_id" : None, "emails": { "$push" : "$email" }, "names": { "$push" : "$name" }
            }
        }
    # I just added loop to make query multiple times same thing
    # In real life senario we will have to grab data from multiple collection and 
    # have to do calculations on top of that
    # so i just added some loop by looking into real world senario

    loop = 100
    for i in range(loop):
        query = mycol.aggregate([
            group
        ])
    res = json.loads(dumps(query))

    query = mycol.find().limit(10)
    data = json.loads(dumps(query))
    api = {

    }
    for i in res:
        api["email_count"] = len(i["emails"])
        api["name_count"] = len(i["names"])
        api["post_ids"] = len(post_ids)
        api["data"] = data
    # finally after all calculations done
    # i am storing the data do redis db with out key
    # so that the next time when user will come it will
    # find the key in redis db hence it will return
    # instead of coming here
    Red.set(cache_key, api)
    return api

# And here i am printing the result by just calling the function
res = get_data()
print(res)