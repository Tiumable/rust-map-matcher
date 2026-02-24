import os
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)


#############################################
# RUSTMAPS SCRAPER (STABIL)
#############################################

def search_rustmaps():

    results = []

    try:

        api_key = 'HIER API KEY EINFÜGEN'  # Optional: API-Key aus Umgebungsvariable oder direkt hier einfügen
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json"
        }

        if api_key:
            headers["X-API-Key"] = api_key

        url = "https://api.rustmaps.com/v4/maps/search?page=0"

        payload = {
            "searchQuery": {
                "size": {
                    "min": 1000,
                    "max": 6000
                }
            }
        }

        r = requests.post(url,
                         json=payload,
                         headers=headers,
                         timeout=10)

        if r.status_code == 200:
            data = r.json()
            
            if "data" in data and data["data"]:
                for map_item in data["data"]:
                    results.append({
                        "seed": str(map_item.get("seed", "Unknown")),
                        "size": str(map_item.get("size", "Unknown")),
                        "match": "100%",
                        "link": map_item.get("url", "https://rustmaps.com"),
                        "name": f"Seed {map_item.get('seed', 'Unknown')} ({map_item.get('size', 'Unknown')})"
                    })
        else:
            print(f"API Error: Status {r.status_code}")
            if r.status_code == 401:
                print("API-Key erforderlich! Setze die Umgebungsvariable RUSTMAPS_API_KEY")

        print("FOUND MAPS:", len(results))

        return results[:20]


    except Exception as e:

        print("ERROR:", e)

        return []


#############################################
# ROUTES
#############################################

@app.route("/")
def home():

    return render_template("index.html")


@app.route("/search",methods=["POST"])
def search():

    print("Search gestartet")

    results = search_rustmaps()


    if not results:

        print("Fallback aktiv")

        results=[{

            "seed":"12345",
            "size":"3500",
            "match":"100%",
            "link":"https://rustmaps.com",
            "name":"Fallback Map"

        }]


    return jsonify({"results":results})


#############################################
# START
#############################################

if __name__=="__main__":

    port=int(os.environ.get("PORT",10000))

    app.run(host="0.0.0.0",
            port=port)
