import os
from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

app = Flask(__name__)

def search_rustmaps(completed_monuments):
    """
    Search rustmaps.com for maps matching the given monument preferences
    """
    base_url = "https://rustmaps.com"
    search_url = f"{base_url}/maps"
    
    try:
        # Make request to rustmaps.com
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find map cards on the page
        map_cards = soup.find_all('div', class_='map-card')
        
        results = []
        
        for card in map_cards[:20]:  # Limit to first 20 results for performance
            try:
                # Extract map information
                map_link = card.find('a', href=True)
                if not map_link:
                    continue
                
                map_url = urljoin(base_url, map_link['href'])
                map_name = map_link.get('title', 'Unknown Map')
                
                # Extract seed from URL or map name
                seed_match = re.search(r'/map/(\d+)', map_url)
                seed = seed_match.group(1) if seed_match else 'Unknown'
                
                # Extract size information
                size_element = card.find('span', string=re.compile(r'\d+'))
                size = size_element.text if size_element else 'Unknown'
                
                # Calculate match percentage based on monument preferences
                match_percentage = calculate_match_percentage(card, completed_monuments)
                
                if match_percentage > 0:  # Only include maps with some match
                    results.append({
                        "seed": seed,
                        "size": size,
                        "match": f"{match_percentage}%",
                        "link": map_url,
                        "name": map_name
                    })
                
            except Exception as e:
                continue  # Skip problematic cards
        
        # Sort by match percentage (descending)
        results.sort(key=lambda x: int(x['match'].replace('%', '')), reverse=True)
        
        return results[:10]  # Return top 10 results
        
    except Exception as e:
        print(f"Error searching rustmaps.com: {e}")
        return []

def calculate_match_percentage(map_card, completed_monuments):
    """
    Calculate match percentage based on monument preferences
    """
    if not completed_monuments:
        return 100  # If no preferences, return 100% match
    
    total_monuments = len(completed_monuments)
    matched_monuments = 0
    
    # Check if map card contains monument information
    card_text = map_card.get_text().lower()
    
    # Map monument names to keywords we might find in the card
    monument_keywords = {
        'launch': ['launch', 'rocket', 'space'],
        'outpost': ['outpost', 'camp'],
        'airfield': ['airfield', 'airport', 'plane'],
        'abandoned_cabins': ['cabin', 'house', 'abandoned'],
        'abandoned_military_base': ['military', 'base', 'bunker'],
        'abandoned_supermarket': ['supermarket', 'store', 'shop'],
        'excavator_pit': ['excavator', 'pit', 'mine'],
        'ferry_terminal': ['ferry', 'terminal', 'boat'],
        'fishing_village': ['fishing', 'village', 'dock'],
        'harbor': ['harbor', 'port', 'ship'],
        'hqm_quarry': ['hqm', 'quarry', 'stone'],
        'junkyard': ['junkyard', 'scrap', 'junk'],
        'arctic_research_base': ['arctic', 'research', 'lab'],
        'lighthouse': ['lighthouse', 'light', 'tower'],
        'military_tunnels': ['tunnel', 'underground', 'military'],
        'mining_outpost': ['mining', 'mine', 'outpost'],
        'missile_silo': ['missile', 'silo', 'rocket']
    }
    
    for monument, preferences in completed_monuments.items():
        if preferences == '':  # User selected "Egal" (doesn't matter)
            continue
            
        keywords = monument_keywords.get(monument, [])
        for keyword in keywords:
            if keyword in card_text:
                matched_monuments += 1
                break
    
    if total_monuments == 0:
        return 100
    
    return int((matched_monuments / total_monuments) * 100)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    # Get all monument form values
    completed_monuments = {
        "launch": request.form.get("launch", ""),
        "outpost": request.form.get("outpost", ""),
        "airfield": request.form.get("airfield", ""),
        "abandoned_cabins": request.form.get("abandoned_cabins", ""),
        "abandoned_military_base": request.form.get("abandoned_military_base", ""),
        "abandoned_supermarket": request.form.get("abandoned_supermarket", ""),
        "excavator_pit": request.form.get("excavator_pit", ""),
        "ferry_terminal": request.form.get("ferry_terminal", ""),
        "fishing_village": request.form.get("fishing_village", ""),
        "harbor": request.form.get("harbor", ""),
        "hqm_quarry": request.form.get("hqm_quarry", ""),
        "junkyard": request.form.get("junkyard", ""),
        "arctic_research_base": request.form.get("arctic_research_base", ""),
        "lighthouse": request.form.get("lighthouse", ""),
        "military_tunnels": request.form.get("military_tunnels", ""),
        "mining_outpost": request.form.get("mining_outpost", ""),
        "missile_silo": request.form.get("missile_silo", "")
    }
    
    # Filter out monuments where user selected "Egal" (empty value)
    completed_monuments = {k: v for k, v in completed_monuments.items() if v != ""}
    
    # Search rustmaps.com
    results = search_rustmaps(completed_monuments)
    
    # If no results from rustmaps.com, fall back to sample data
    if not results:
        results = [
            {
                "seed": "12345",
                "size": "3500",
                "match": "100%",
                "link": "https://rustmaps.com",
                "name": "Sample Map 1"
            },
            {
                "seed": "88822", 
                "size": "4000",
                "match": "95%",
                "link": "https://rustmaps.com",
                "name": "Sample Map 2"
            },
            {
                "seed": "54321",
                "size": "3800", 
                "match": "90%",
                "link": "https://rustmaps.com",
                "name": "Sample Map 3"
            }
        ]
    
    return jsonify({"results": results})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)



