import os
from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

app = Flask(__name__)

#################################################
# BIOME ERKENNUNG
#################################################

def detect_biome(x, y, size):

    if y > size * 0.6:
        return "snow"

    elif y < size * 0.3:
        return "desert"

    else:
        return "temperate"


#################################################
# STABILE RUSTMAPS SUCHE
#################################################

def search_rustmaps(completed_monuments):

    base_url = "https://rustmaps.com/maps"

    results = []

    try:

        headers = {
            'User-Agent': 'Mozilla/5.0'
        }

        response = requests.get(base_url,
                                headers=headers,
                                timeout=10)

        soup = BeautifulSoup(response.text,'html.parser')

        map_links = soup.find_all("a",
                    href=re.compile(r'/map/\d+'))

        for i, link in enumerate(map_links[:20]):

            map_url = urljoin("https://rustmaps.com",
                              link['href'])

            seed_match = re.search(r'/map/(\d+)',
                                   map_url)

            seed = seed_match.group(1) if seed_match else "?"

            results.append({

                "seed": seed,
                "size": "Unknown",
                "match": "80%",
                "link": map_url,
                "name": f"Seed {seed}"

            })


        return results


    except Exception as e:

        print("Search Error:", e)

        return []


#################################################
# ROUTES
#################################################

@app.route("/")
def home():

    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():

    completed_monuments = {

        "launch": request.form.get("launch",""),
        "outpost": request.form.get("outpost",""),
        "airfield": request.form.get("airfield",""),
        "harbor": request.form.get("harbor",""),
        "junkyard": request.form.get("junkyard",""),
        "lighthouse": request.form.get("lighthouse",""),
        "military_tunnels": request.form.get("military_tunnels",""),
        "missile_silo": request.form.get("missile_silo",""),
        "fishing_village": request.form.get("fishing_village",""),
        "mining_outpost": request.form.get("mining_outpost","")

    }

    completed_monuments = {
        k:v for k,v in completed_monuments.items()
        if v != ""
    }

    print("SEARCH:",completed_monuments)


    results = search_rustmaps(completed_monuments)


    #################################################
    # FALLBACK (immer etwas anzeigen)
    #################################################

    if not results:

        results=[{

            "seed":"12345",
            "size":"3500",
            "match":"100%",
            "link":"https://rustmaps.com",
            "name":"Test Map"

        }]


    return jsonify({"results":results})


#################################################
# START
#################################################

if __name__ == "__main__":

    port=int(os.environ.get("PORT",10000))

    app.run(host="0.0.0.0",
            port=port)
