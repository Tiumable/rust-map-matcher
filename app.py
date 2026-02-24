import os
from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

app = Flask(__name__)

def search_rustmaps(completed_monuments, api_number=None):
    """
    Search for maps matching the given monument preferences
    """
    # Use custom API Number if provided, otherwise default to rustmaps.com
    if api_number and api_number.strip():
        # Construct URL from API number
        base_url = f"https://rustmaps.com/map/{api_number}"
    else:
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
        
        # Debug: Print the HTML structure to understand the page layout
        print("=== RUSTMAPS.COM HTML STRUCTURE ===")
        print("Page title:", soup.title.string if soup.title else "No title")
        
        # Try different selectors for map cards
        map_cards = []
        
        # Method 1: Look for common map container classes
        possible_selectors = [
            'div.map-card',
            'div.map-item', 
            'div.card',
            'div.map',
            'a[href*="/map/"]',
            'div[class*="map"]',
            'article',
            'section'
        ]
        
        for selector in possible_selectors:
            cards = soup.select(selector)
            if cards:
                print(f"Found {len(cards)} elements with selector: {selector}")
                map_cards.extend(cards)
                if len(map_cards) >= 10:  # We have enough
                    break
        
        # If no cards found with selectors, try finding all links to maps
        if not map_cards:
            map_links = soup.find_all('a', href=re.compile(r'/map/\d+'))
            print(f"Found {len(map_links)} map links")
            for link in map_links[:20]:
                # Create a mock card structure
                map_cards.append(link)
        
        results = []
        
        for i, card in enumerate(map_cards[:20]):  # Limit to first 20 results
            try:
                # Extract map information based on what type of element we have
                if hasattr(card, 'name') and card.name == 'a':
                    # This is a link element
                    map_link = card
                    map_url = urljoin(base_url, map_link['href'])
                    map_name = map_link.get('title') or map_link.get_text().strip() or f"Map {i+1}"
                else:
                    # This is a container element
                    map_link = card.find('a', href=True)
                    if not map_link:
                        continue
                    map_url = urljoin(base_url, map_link['href'])
                    map_name = map_link.get('title') or map_link.get_text().strip() or f"Map {i+1}"
                
                # Extract seed from URL
                seed_match = re.search(r'/map/(\d+)', map_url)
                seed = seed_match.group(1) if seed_match else f"seed_{i+1}"
                
                # Extract size information - look for numbers in the text
                card_text = card.get_text().lower() if hasattr(card, 'get_text') else map_name.lower()
                size_match = re.search(r'(\d{3,4})', card_text)
                size = size_match.group(1) + "m" if size_match else "Unknown"
                
                # Calculate match percentage based on monument preferences
                match_percentage = calculate_match_percentage(card, completed_monuments)
                
                # Always include results to show we're getting real data
                results.append({
                    "seed": seed,
                    "size": size,
                    "match": f"{match_percentage}%",
                    "link": map_url,
                    "name": map_name[:50]  # Limit name length
                })
                
                if len(results) >= 10:  # Limit to 10 results
                    break
                
            except Exception as e:
                print(f"Error processing card {i}: {e}")
                continue
        
        # Sort by match percentage (descending) if we have matches
        if results and any('%' in r['match'] for r in results):
            results.sort(key=lambda x: int(x['match'].replace('%', '')), reverse=True)
        
        print(f"=== FOUND {len(results)} RESULTS ===")
        for result in results[:3]:
            print(f"  - {result['name']} (Seed: {result['seed']}, Match: {result['match']})")
        
        return results if results else []
        
    except Exception as e:
        print(f"Error searching rustmaps.com: {e}")
        import traceback
        traceback.print_exc()
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
    
    # Get custom API Number from form
    api_number = request.form.get("apiNumber", "").strip()
    
    # Filter out monuments where user selected "Egal" (empty value)
    completed_monuments = {k: v for k, v in completed_monuments.items() if v != ""}
    
    # Search with custom API Number
    results = search_rustmaps(completed_monuments, api_number)
    
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



