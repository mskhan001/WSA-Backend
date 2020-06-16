from flask import Flask, jsonify
import requests
import json

app = Flask(__name__)

API_KEY = "AIzaSyDKyC8k5UNUx5tQ3wDJNz5ipzrsGQ_4zCU"


@app.route("/")
def findPlaces(loc=("26.869", "80.960"), radius=500):
    lat, lng = loc
    sahithi = []
    type = "schools"
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&type={type}&key={API_KEY}".format(
        lat=lat, lng=lng, radius=radius, type=type, API_KEY=API_KEY)
    print(url)
    response = requests.get(url)
    res = json.loads(response.text)
    print(len(res["results"]))
    data = {}
    i = 0
    for result in res["results"]:
        info = ";".join(map(str, [result["name"], result["geometry"]["location"]
                                  ["lat"], result["geometry"]["location"]["lng"], result["place_id"]]))
        data[i] = info
        i = i+1

    return data


if __name__ == '__main__':
    app.run(debug=True)
