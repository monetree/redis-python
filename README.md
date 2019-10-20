# Steps to run this app locally

1. install redis (`https://redis.io/`)
2. install mongodb (`https://www.mongodb.com/`)
3. create database with named `dummy` in mongodb
4. dump the data `comments.csv` or `comments.json` into db using `mongoexport --db=dummy --collection=comments --out=comments.json` command
5. install requiremets using `pip install -r requirements.txt` (You can use virtualenv also as i am using)
5. run `python app.py` in current directory

        
