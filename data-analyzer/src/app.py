#!/usr/bin/env python3

from flask import Flask, request, Response
import requests
from textblob import TextBlob
import sqlite3
import json
import pika, os
import threading
app = Flask(__name__)

conn = sqlite3.connect('database1.db')
conn.execute('CREATE TABLE IF NOT EXISTS sentiment_movies (name TEXT, sentiment DECIMAL(10,10))')
conn.close()

def perform_sentiment_analysis(input):
    blob = TextBlob(input)
    polarity = blob.sentiment.polarity
    with sqlite3.connect("database1.db") as db_connection:
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO sentiment_movies (name,sentiment) VALUES (?,?)",(input, polarity))
        db_connection.commit()

def get_data_from_collector():
    with sqlite3.connect("database1.db") as db_connection:
        cursor = db_connection.cursor()
        cursor.execute("DELETE from sentiment_movies;")
        db_connection.commit()
    r = requests.get('https://data-collector-1014dc8647ce.herokuapp.com/movies')
    json_r = r.json()
    for element in json_r:
        perform_sentiment_analysis(element[0])






        



@app.route("/")
def main():
    return '''
     <form action="/echo_user_input" method="POST">
	<h1>ANALYZER12</h1>
         <input name="user_input">
         <input type="submit" value="Submit!">
     </form>
     '''

@app.route("/echo_user_input", methods=["POST"])
def echo_input():
    input_text = request.form.get("user_input", "")
    return "You entered: " + input_text

@app.route("/check_movies", methods=["GET"])
def check_movies():
    get_data_from_collector()

@app.route("/positive_movies", methods=["GET"])
def positive_movies():
    print("in pos mpv")
    print("threads:")
    for thread in threading.enumerate(): 
        print(thread.name)
    print("end threads")
    with sqlite3.connect("database1.db") as connection:
        cur = connection.cursor()
        cur.execute("SELECT name FROM sentiment_movies WHERE sentiment > 0.0")
        print("after cur execute")
        rows = cur.fetchall()
        print("json is " + json.dumps(rows))
        return Response(json.dumps(rows),  mimetype='application/json')

@app.route("/neutral_movies", methods=["GET"])
def neutral_movies():
    with sqlite3.connect("database1.db") as connection:
        cur = connection.cursor()
        cur.execute("SELECT name FROM sentiment_movies WHERE sentiment == 0.0")
        rows = cur.fetchall()
        return Response(json.dumps(rows),  mimetype='application/json')
    
@app.route("/negative_movies", methods=["GET"])
def negative_movies():
    with sqlite3.connect("database1.db") as connection:
        cur = connection.cursor()
        cur.execute("SELECT name FROM sentiment_movies WHERE sentiment < 0.0")
        rows = cur.fetchall()
        return Response(json.dumps(rows),  mimetype='application/json')

def StartConsuming():
    # Access the CLODUAMQP_URL environment variable and parse it (fallback to localhost)
    url = 'amqp://sjqvozfu:csP8z9MrrJfNrTFVIqLI76FTZ9iCvBmk@gull.rmq.cloudamqp.com/sjqvozfu'
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel() # start a channel
    channel.queue_declare(queue='read-notif') # Declare a queue
    def callback(ch, method, properties, body):
        print("in callback")
        get_data_from_collector()
    print(' [*] Waiting for messages:', flush=True)
    channel.basic_consume('read-notif',
                        callback,
                        auto_ack=True)
    os.sleep(60*60*3)
    

    connection.close()

if __name__ == '__main__':
    t1 = threading.Thread(target=StartConsuming, name="consume_thread", daemon=True)
    t1.start()
    print("Running app")
    app.run(host='0.0.0.0', port=9892)

