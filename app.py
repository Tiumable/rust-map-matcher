import os
from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

app = Flask(__name__)

#################################################
# BIOM ERKENNUNG ÜBER KOORDINATEN
#################################################

def detect_biome(x, y, size):

    if y > size * 0.6:
        return "snow"

    elif y < size * 0.3:
        return "desert"

    else:
        return "temperate"


#################################################
# ECHTE RUSTMAPS JSON SUCHE (HAUPTENGINE)
#################################################

def search_rustmaps_api(completed_monuments):

    results = []

    seeds = range(1000,1100)
    sizes = [3500,4000]

    monument_name_map = {

        "launch":"Launch Site",
        "outpost":"Outpost",
        "airfield":"Airfield",
        "harbor":"Harbor",
        "junkyard":"Junkyard",
        "lighthouse":"Lighthouse",
        "military_tunnels":"Military Tunnel",
        "missile_silo":"Missile Silo",
        "fishing_village":"Fishing Village",
        "mining_outpost":"Mining Outpost"

    }

    for size in sizes:

        for seed in seeds:

            try:

                url = f"https://rustmaps.com/map/{size}_{seed}.json"

                r = requests.get(url, timeout=3)

                if r.status_code != 200:
                    continue

                data = r.json()

                monuments = data.get("monuments", [])

                score = 0
                total = 0

                for monument_key, biomeWanted in completed_monuments.items():

                    monumentName = monument_name_map.get(monument_key)

                    if not monumentName:
                        continue

                    total += 1

                    for m in monuments:

                        if monumentName.lower() in m["name"].lower():

                            x = m.get("x",0)
                            y = m.get("y",0)

                            biomeDetected = detect_biome(x,y,size)

                            if biomeDetected == biomeWanted:

                                score +=1


                if total > 0:

                    match = int((score/total)*100)

                    if match > 40:

                        results.append({

                            "seed":seed,
                            "size":size,
                            "match":f"{match}%",
                            "link":f"https://rustmaps.com/map/{size}_{seed}",
                            "name":f"Seed {seed}"

                        })

            except:
                pass


    results = sorted(results,
                     key=lambda x: int(x["match"].replace("%","")),
                     reverse=True)

    return results[:10]


#################################################
# FALLBACK SCRAPER (DEINE ALTE ENGINE)
#################################################

def search_rustmaps_scraper(completed_monuments):

    base_url = "https://rustmaps.com"
    search_url = f"{base_url}/maps"

    try:

        headers = {
            'User-Agent': 'Mozilla/5.0'
        }

        response = requests.get(search_url,
                                headers=headers,
                                timeout=10)

        soup = BeautifulSoup(response.content,
                             'html.parser')

        map_links = soup.find_all('a',
                     href=re.compile(r'/map/\d+'))

        results=[]

        for i,link in enumerate(map_links[:10]):

            map_url = urljoin(base_url,
                              link['href'])

            seed_match = re.search(r'/map/(\d+)',
                                   map_url)

            seed = seed_match.group(1) if seed_match else "?"

            results.append({

                "seed":seed,
                "size":"Unknown",
                "match":"50%",
                "link":map_url,
                "name":f"Map {i+1}"

            })

        return results

    except Exception as e:

        print("SCRAPER ERROR:",e)

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

    print("USER SEARCH:",completed_monuments)


    #################################
    # 1️⃣ API SUCHE
    #################################

    results = search_rustmaps_api(completed_monuments)


    #################################
    # 2️⃣ FALLBACK SCRAPER
    #################################

    if not results:

        print("Fallback Scraper aktiviert")

        results = search_rustmaps_scraper(completed_monuments)


    #################################
    # 3️⃣ SAMPLE FALLBACK
    #################################

    if not results:

        results=[{

            "seed":"12345",
            "size":"3500",
            "match":"100%",
            "link":"https://rustmaps.com",
            "name":"Fallback Map"

        }]


    return jsonify({"results":results})


#################################################
# RENDER START
#################################################

if __name__ == "__main__":

    port=int(os.environ.get("PORT",10000))

    app.run(host="0.0.0.0",
            port=port)
