#!/usr/bin/env python3

from flask import Flask, request, render_template
import requests
app = Flask(__name__)

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/echo_user_input", methods=["POST"])
def echo_input():
    input_text = request.form.get("user_input", "")
    return "You entered: " + input_text

@app.route("/send_get_request", methods=["POST"])
def send_get_request():
    select_value = request.form.get("emotion-select")
    print(select_value)
    match select_value:
        case "1":
            print("selected1")
            return load_movies('https://data-analyzer-354624b71875.herokuapp.com/positive_movies', "Positive")
            print("selected")
        case "2":
            return load_movies('https://data-analyzer-354624b71875.herokuapp.com/neutral_movies', "Neutral")
        case "3":
            return load_movies('https://data-analyzer-354624b71875.herokuapp.com/negative_movies', "Negative")


def load_movies(url, type):
    movie_list = []
    movie_list.append(type)
    print("url: "+ url)
    r = requests.get(url)
    print("r" + r)
    json_r = r.json()
    for element in json_r:
        movie_list.append(element[0])
    for element in movie_list:
        print(element)
    return render_template('view.html', input=movie_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9893)
