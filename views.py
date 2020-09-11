from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import logging
# from songs import app
app=Flask(__name__)

logging.basicConfig(level=logging.DEBUG)



db=SQLAlchemy(app)


class Upload(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	title=db.Column(db.String(500))
	artist=db.Column(db.String(200))
	album=db.Column(db.String(200))
	# song=db.Column(db.LargeBinary)

@app.route('/')
def index():
	song_list=Upload.query.all()
	return render_template("index.html",song_list=song_list)


@app.route('/upload',methods=['GET','POST'])
def upload():
	if request.method=='POST':
		logging.debug('if request.method ==POST: is TRUE')
		# file=request.files['file']
		title=request.form.get['title']
		album=request.form.get['album']
		artist=request.form.get['artist']
		new_song=Upload(title="title",album="album",artist="artist")
		db.session.add(new_song)
		db.session.commit()
	return render_template("upload.html")
	# return redirect(url_for("index"))




if __name__=='__main__':
	app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.sqlite'
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
	db.create_all()
	app.run(debug=True)