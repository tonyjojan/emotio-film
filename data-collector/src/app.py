#!/usr/bin/env python3

from flask import Flask, request, jsonify, Response
from urllib.request import urlopen
import sqlite3
import ssl
import json
import requests
import pika, os

app = Flask(__name__)
from bs4 import BeautifulSoup
import re 
HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}

# Access the CLODUAMQP_URL environment variable and parse it (fallback to localhost)
url = 'amqp://sjqvozfu:csP8z9MrrJfNrTFVIqLI76FTZ9iCvBmk@gull.rmq.cloudamqp.com/sjqvozfu'
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel() # start a channel
channel.queue_declare(queue='read-notif') # Declare a queue
channel.basic_publish(exchange='',
                      routing_key='read-notif',
                      body='Hello CloudAMQP!')

print(" [x] Sent 'Hello World!'")
connection.close()



conn = sqlite3.connect('database.db')
print("Opened database successfully");
conn.execute('CREATE TABLE IF NOT EXISTS movies (name TEXT)')
print ("Table created successfully");
conn.close()
ssl._create_default_https_context = ssl._create_unverified_context


def scrape():
    r = requests.get('http://www.imdb.com/chart/top/', headers=HEADERS)
    # url = "http://www.imdb.com/chart/top/"
    # page = urlopen(url)
    # html_raw = page.read()
    # html = html_raw.decode("utf-8")
    # print(html)
    with sqlite3.connect("database.db") as db_connection:
        cursor = db_connection.cursor()
        cursor.execute("DELETE from movies;")
        db_connection.commit()
    soup = BeautifulSoup(r.text, 'html.parser')
    movie_names = soup.find_all('h3', class_='ipc-title__text')
    for movie_name in movie_names:
        #remove movie number from name
        pattern = r'[0-9]'
        movie_formatted_with_prefix = re.sub(pattern, '', movie_name.text)
        movie_name_cleaned = movie_formatted_with_prefix[2:]
        #add to DB
        with sqlite3.connect("database.db") as db_connection:
            cursor = db_connection.cursor()
            cursor.execute("INSERT INTO movies (name) VALUES (?)",(movie_name_cleaned,))
            db_connection.commit()
    connection = pika.BlockingConnection(params)
    channel = connection.channel() # start a channel
    channel.queue_declare(queue='read-notif') # Declare a queue
    channel.basic_publish(exchange='',
            routing_key='read-notif',
            body='now analyze!')
    print(" [x] Sent 'analyzedirec'")
    connection.close()

@app.route("/")
def main():
    return '''
     <form action="/echo_user_input" method="POST">
        <h1>COLLECTOR2</h1> 
	<input name="user_input">
         <input type="submit" value="Submit!">
     </form>
     '''

@app.route("/echo_user_input", methods=["POST"])
def echo_input():
    input_text = request.form.get("user_input", "")
    return "You entered: " + input_text

@app.route("/test_endpoint", methods=["GET"])
def test_endpt():
    return jsonify({
        'status' : 'alive'
    })

@app.route("/movies", methods=["GET"])
def getMovies():
    scrape()
    with sqlite3.connect("database.db") as connection:
        cur = connection.cursor()
        cur.execute("SELECT * FROM movies")
        rows = cur.fetchall()
        return Response(json.dumps(rows),  mimetype='application/json')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9891)
