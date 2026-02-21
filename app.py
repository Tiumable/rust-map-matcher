from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():

    # Get all monument form values
    launch = request.form.get("launch")
    outpost = request.form.get("outpost")
    airfield = request.form.get("airfield")
    abandoned_cabins = request.form.get("abandoned_cabins")
    abandoned_military_base = request.form.get("abandoned_military_base")
    abandoned_supermarket = request.form.get("abandoned_supermarket")
    excavator_pit = request.form.get("excavator_pit")
    ferry_terminal = request.form.get("ferry_terminal")
    fishing_village = request.form.get("fishing_village")
    harbor = request.form.get("harbor")
    hqm_quarry = request.form.get("hqm_quarry")
    junkyard = request.form.get("junkyard")
    arctic_research_base = request.form.get("arctic_research_base")
    lighthouse = request.form.get("lighthouse")
    military_tunnels = request.form.get("military_tunnels")
    mining_outpost = request.form.get("mining_outpost")
    missile_silo = request.form.get("missile_silo")

    # Sample results with more diverse data
    results = [

        {
            "seed":12345,
            "size":3500,
            "match":"100%",
            "link":"https://rustmaps.com"
        },

        {
            "seed":88822,
            "size":4000,
            "match":"95%",
            "link":"https://rustmaps.com"
        },

        {
            "seed":54321,
            "size":3800,
            "match":"90%",
            "link":"https://rustmaps.com"
        },

        {
            "seed":99999,
            "size":4200,
            "match":"85%",
            "link":"https://rustmaps.com"
        },

        {
            "seed":77777,
            "size":3600,
            "match":"80%",
            "link":"https://rustmaps.com"
        }

    ]

    return {"results":results}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)



