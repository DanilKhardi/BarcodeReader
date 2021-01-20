from flask import Flask, request
from typing import NamedTuple

app = Flask(__name__)

port_dictionary = {'000042819716900001': 'port 1', '4607032891055': 'port 2'}


# test = NamedTuple('000042819716900001' : 'port 1', '4607032891055' : 'port 2')

@app.route("/barcode", methods=['POST', 'GET'])
def getInfo():
    if request.method == 'POST':
        text_input = request.form
        text_input = list(text_input)[0]
        print(port_dictionary[text_input])
        return str(text_input)


if __name__ == '__main__':
    app.run(debug=True)
