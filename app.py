import os
from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


#############################################
# RUSTMAPS SCRAPER (STABIL)
#############################################

def search_rustmaps():

    results = []

    try:

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        url = "https://rustmaps.com"

        r = requests.get(url,
                         headers=headers,
                         timeout=10)

        soup = BeautifulSoup(r.text,"html.parser")

        links = soup.find_all("a")

        for link in links:

            href = link.get("href","")

            if "/map/" in href:

                full_link = "https://rustmaps.com"+href

                seed="Unknown"
                size="Unknown"

                parts = href.split("/")

                if len(parts) > 2:

                    map_id = parts[-1]

                    if "_" in map_id:

                        size,seed = map_id.split("_")

                results.append({

                    "seed":seed,
                    "size":size,
                    "match":"90%",
                    "link":full_link,
                    "name":f"Seed {seed} ({size})"

                })


        print("FOUND MAPS:",len(results))

        return results[:20]


    except Exception as e:

        print("ERROR:",e)

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
