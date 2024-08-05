from flask import Flask, render_template, request
import ast
import requests

app = Flask(__name__)
url = "https://api.npoint.io/674f5423f73deab1e9a7"
responses = requests.get(url).json()

@app.route("/")
def get_all_posts():
    return render_template("index.html", responses=responses)

@app.route("/post")
def get_clicked_post():

    response = request.args.get('response')
    response = ast.literal_eval(response)
    return render_template("post.html", response=response)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run()