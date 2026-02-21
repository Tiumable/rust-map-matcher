from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():

    launch = request.form.get("launch")
    outpost = request.form.get("outpost")
    airfield = request.form.get("airfield")

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
            "match":"80%",
            "link":"https://rustmaps.com"
        }

    ]

    return {"results":results}


app.run()