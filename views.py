from flask import Flask, render_template, request, redirect, url_for,send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import logging
from io import BytesIO
from slugify import slugify
import flask_whooshalchemyplus as wa
from flask_whooshalchemyplus import index_all
# from songs import app
app=Flask(__name__)

APP_ROOT=os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER=os.path.join(APP_ROOT,'static')
logging.basicConfig(level=logging.DEBUG)




db=SQLAlchemy(app)


class Upload(db.Model):
	__tablename__='Upload'
	__searchable__=["title","artist"]
	id=db.Column(db.Integer,primary_key=True)
	title=db.Column(db.String(500))
	artist=db.Column(db.String(200))
	album=db.Column(db.String(200))
	song=db.Column(db.LargeBinary)
	filename=db.Column(db.String(300))
	slug=db.Column(db.String())

	def __init__(self, *args, **kwargs):
		if not 'slug' in kwargs:
			kwargs['slug'] = slugify(kwargs.get('title', ''))
			super().__init__(*args, **kwargs)
	def __repr__(self):
		return self.title

app.config['WHOOSH_BASE']="whoosh"

wa.whoosh_index(app, Upload)


@app.route('/')
def index():
	song_list=Upload.query.all()
	return render_template("index.html",song_list=song_list)

@app.route('/<song_slug>')
def index_detail(song_slug):
	song=Upload.query.filter_by(slug=song_slug).first()
	return render_template("song_detail.html",song=song)

@app.route('/delete/<song_slug>')
def delete(song_slug):
	song=Upload.query.filter_by(slug=song_slug).first()
	db.session.delete(song)
	db.session.commit()
	return redirect(url_for("index"))


@app.route('/upload',methods=['GET','POST'])
def upload():
	if request.method=='POST':
		logging.debug('if request.method ==POST: is TRUE')
		file=request.files['file']
		title=request.form.get('title')
		album=request.form.get('album')
		artist=request.form.get('artist')
		filename=secure_filename(file.filename)
		print("&&&&&&&&&&&&&&&&&")
		print(filename)
		print("&&&&&&&&&&&&&&&&&&&")
		# file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
		new_song=Upload(title=title,song=file.read(),album=album,artist=artist,filename=filename)
		db.session.add(new_song)
		db.session.commit()
		return redirect(url_for("index"))
	return render_template("upload.html")

@app.route('/search')
def search():
	song=Upload.query.whoosh_search(request.args.get('query')).all()
	print("*******************")
	print(song)
	print("*******************")
	return render_template('index.html',song=song)

@app.route('/download/<song_filename>')
def download(song_filename):
	file_data=Upload.query.filter_by(filename=song_filename).first()
	return send_file(BytesIO(file_data.song),mimetype="audio/mp3",attachment_filename=file_data.filename,as_attachment=True,)




if __name__=='__main__':
	app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///songs.db'
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
	app.config['DEBUG']=True
	app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
	db.create_all()
	app.run(debug=True)