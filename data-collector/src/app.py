#!/usr/bin/env python3

from flask import Flask, request, jsonify

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9891)
