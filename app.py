import warnings
from flask import Flask, render_template, request, jsonify
import wikipedia
import arxiv
import requests
from deep_translator import GoogleTranslator
from bs4 import GuessedAtParserWarning

warnings.filterwarnings("ignore", category=GuessedAtParserWarning)

app = Flask(__name__)

# --- MADDA 1: DUCKDUCKGO (Ultra Fast & Free) ---
def get_duckduckgo(query_en):
    try:
        url = f"https://api.duckduckgo.com/?q={query_en}&format=json&no_html=1"
        res = requests.get(url, timeout=3).json()
        return res.get("AbstractText")
    except:
        return None

# --- MADDA 2: ARXIV (Science & Tech) ---
def get_arxiv(query_en):
    try:
        search = arxiv.Search(query=query_en, max_results=1)
        for result in search.results():
            return f"Qorannoo: {result.title}. {result.summary[:400]}..."
        return None
    except:
        return None

# --- BRAIN GURMAA'E ---
def ai_brain(query):
    if not query: return "Maaloo waan tokko barreessi."
    
    try:
        # Gara English tti hiikuu
        query_en = GoogleTranslator(source='auto', target='en').translate(query)
        
        result_en = None
        
        # 1. Dura DuckDuckGo yaali (Saffisaaf)
        result_en = get_duckduckgo(query_en)
        
        # 2. Yoo saayinsii ta'e ArXiv dabali
        science_keywords = ["science", "theory", "research", "physics", "algorithm", "ai"]
        if any(k in query_en.lower() for k in science_keywords):
            arxiv_res = get_arxiv(query_en)
            if arxiv_res: result_en = arxiv_res

        # 3. Yoo DuckDuckGo dhabame Wikipedia yaali
        if not result_en:
            wikipedia.set_lang("en")
            search_res = wikipedia.search(query_en)
            if search_res:
                result_en = wikipedia.summary(search_res[0], sentences=3)
        
        if not result_en:
            return f"Dhiifama, waa'ee '{query}' odeeffannoo gahaa dhabeera."

        # Gara Afaan Oromootti hiikuu
        return GoogleTranslator(source='en', target='om').translate(result_en)

    except Exception as e:
        print(f"Error: {e}")
        return "Rakkoon quunnamtii uumameera."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def ask():
    data = request.get_json()
    user_msg = data.get("message", "")
    response = ai_brain(user_msg)
    return jsonify({"success": True, "response": response})

if __name__ == '__main__':
    app.run(debug=True)
