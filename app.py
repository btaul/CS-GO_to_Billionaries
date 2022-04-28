from flask import Flask
from flaskext import mysql
from web import app

app = Flask(__name__)

mysql = mysql()
app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'CS4400GP9'
app.config['MYSQL_DATABASE_HOST'] = 'csgo1m.cj3rigewkoph.us-east-2.rds.amazonaws.com'
app.config['MYSQL_DATABASE_PORT'] = '3306'
app.config['MYSQL_DATABASE_DB'] = 'CSGO2M'


mysql.init(app)


if __name__ == '__main__':
    app.run(debug=True)