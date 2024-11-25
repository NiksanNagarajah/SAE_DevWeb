from flask import Flask, render_template
from flask_mysqldb import MySQL

app = Flask(__name__)


app.config["SECRET_KEY"] = 'e9fb1c87-3809-4891-88d2-abfcde76d817'
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

app.config['MYSQL_HOST'] = 'servinfo-maria'
app.config['MYSQL_USER'] = 'nagarajah'
app.config['MYSQL_PASSWORD'] = 'nagarajah'
app.config['MYSQL_DB'] = 'DBnagarajah'

mysql=MySQL(app)

