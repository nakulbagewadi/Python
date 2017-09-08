#!flask/bin/python

from app import app

app.run(debug = True,
        host = '0.0.0.0',
        port = 1234)
		
		
'''
How to run flask virtual enviornment for this project:

Step 1: $export FLASK_APP=run.py
Step 2: $flask run
Step 3: Go to http://localhost:7777/homepage

'''