from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict')
def generate():
    return render_template('predict.html')

@app.route('/image')
def image():
    return render_template('image.html')

@app.route('/create')
def create():
    return render_template('create.html')


