from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
data = SQLAlchemy(app)

class Data(data.Model):
	uid = data.Column(data.Integer, primary_key=True)
	username = data.Column(data.String(32), unique=False, nullable=True)
	time = data.Column(data.Integer, unique=False, nullable=False)
	weather = data.Column(data.String(512), unique=False, nullable=True)

	def __repr__(self):
		return f"Data( {self.uid}, '{self.username}', {self.time}, Weather<> )"

data.drop_all()
data.create_all()
