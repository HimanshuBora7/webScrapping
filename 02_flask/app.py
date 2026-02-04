from flask import Flask,request

app = Flask(__name__)

@app.route("/")
def home():
    return 'hello user! this is my first flask app '

@app.route("/about")
def about():
    return 'you are on about page '

@app.route("/contact")
def contact():
    return 'uhh, u wanna contact us !!'
# route should be unique 
# routes should be readable 
# route should always should return something 

@app.route("/submit", methods=["GET","POST"])
def submit():
    if request.method == "POST":
        return "you send data"
    else:
        return "You are only viewing the form"