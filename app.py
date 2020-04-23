from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/ping/', methods=['GET'])
def respond():

    response = {}
    response["Status"] = "Running"
    return jsonify(response)


@app.route('/')
def index():
    return "<h1>Welcome to application server !</h1>"

if __name__ == '__main__':
    app.run()