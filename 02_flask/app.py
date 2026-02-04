# from flask import Flask,request

# app = Flask(__name__)

# @app.route("/")
# def home():
#     return 'hello user! this is my first flask app '

# @app.route("/about")
# def about():
#     return 'you are on about page '

# @app.route("/contact")
# def contact():
#     return 'uhh, u wanna contact us !!'
# # route should be unique 
# # routes should be readable 
# # route should always should return something 

# @app.route("/submit", methods=["GET","POST"])
# def submit():
#     if request.method == "POST":
#         return "you send data"
#     else:
#         return "You are only viewing the form"

from flask import Flask,request,redirect,url_for,session,Response

app = Flask(__name__)
app.secret_key ="supersecret"
# homepage login page 
@app.route("/",methods =["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "123":
            session["user"] = username # store in session 
            return redirect(url_for("welcome"))
        else :
            return Response("in valid credentials", mimetype="text/plain") #text/html
    return '''
    <h2> Login page <h2>
    <form method ="POST">
    Username: <input type="text" name="username"><br>
    Password: <input type="password"  name="password"><br>
    <input type="submit" value="Login">
    </form>

'''

# welcome page(after login )
@app.route("/welcome")
def welcome():
    if "user" in session:
        return f''' 
<h2>Welcome, {session["user"]}</h2>
<a href={url_for('logout')}>Logout</a>
'''
    return redirect(url_for("login"))

#logout route 
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))