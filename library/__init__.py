from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import pyotp

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://fubsi:1234@localhost:3306/hwpdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['F2A_SECRET_KEY'] = "THISISMYLIBRARYSECRET"  # Example secret key for 2FA 
app.secret_key = "THISISMYLIBRARYSECRET"  # Example secret key for Flask sessions
# TO FIND IT USE FLASK_UNSIGN:
# flask-unsign --unsign --cookie 'eyJiZW51dHplcklkIjoiMSIsImJlbnV0emVybmFtZSI6ImZ1YnNpIn0.aEu4EA.vP_S3Pes-qzQQ8bdl9BmQAaWpxE' --no-literal-eval -w pws.txt

db = SQLAlchemy(app)
totp = pyotp.TOTP(app.config['F2A_SECRET_KEY'])