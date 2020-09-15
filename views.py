from flask import Flask, render_template, request, redirect, url_for,send_file
from flask_sqlalchemy import SQLAlchemy
# from flask_wtf import FlaskForm
from sqlalchemy import and_, or_, not_
from werkzeug.utils import secure_filename
import os
import logging
from io import BytesIO
from slugify import slugify



app=Flask(__name__)

APP_ROOT=os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER=os.path.join(APP_ROOT,'static/uploads')
logging.basicConfig(level=logging.DEBUG)
ALLOWED_EXTENSIONS = {'mp3'}
app.secret_key = os.urandom(24)

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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
	os.remove(os.path.join(app.config['UPLOAD_FOLDER'],song.filename))
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
		
		if file and allowed_file(file.filename):
			file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
			new_song=Upload(title=title,song=file.read(),album=album,artist=artist,filename=filename)
			db.session.add(new_song)
			db.session.commit()
			return redirect(url_for("index"))
		else:
			feedback="Upload only .mp3 files"
			return render_template("upload.html",feedback=feedback)
	return render_template("upload.html")



@app.route('/search')
def search():
	serch=request.args.get('query')
	song_list=Upload.query.filter(or_(Upload.filename.contains(serch),
								Upload.album.contains(serch),
								Upload.artist.contains(serch))).all()
	return render_template('index.html',song_list=song_list)

@app.route('/download/<song_filename>')
def download(song_filename):
	file_data=Upload.query.filter_by(filename=song_filename).first()
	return send_file(BytesIO(file_data.song),mimetype="audio/mp3",attachment_filename=file_data.filename,as_attachment=True,)



if __name__=='__main__':
	app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///songs.db'
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
	app.config['DEBUG']=True
	app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
	app.config['ALLOWED_EXTENSIONS']=".mp3"
	db.create_all()
	app.run(debug=True)