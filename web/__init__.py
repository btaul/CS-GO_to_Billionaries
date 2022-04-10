from flask import Flask
import pymysql

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretkey'

connection = pymysql.connect(
     host='csgo1m.cj3rigewkoph.us-east-2.rds.amazonaws.com',
     user='admin',
     password='CS4400GP9',
     port=3306,
     database='CSGO2M'
)
# test connection
cursor = connection.cursor()
query = "SELECT team_name from teams"
cursor.execute(query)
data = cursor.fetchone()
print(data)



from web import routes