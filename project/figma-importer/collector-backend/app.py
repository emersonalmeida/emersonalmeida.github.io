from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import time

app = Flask(__name__)
CORS(app)

REQUEST_TIMEOUT = 10
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9"
}

def safe_get(url, timeout=REQUEST_TIMEOUT, max_retries=2):
    last_exc = None
    for attempt in range(max_retries):
        try:
            r = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
            return r
        except Exception as exc:
            last_exc = exc
            time.sleep(0.25)
    raise last_exc

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "missing url param"}), 400
    try:
        r = safe_get(url)
        return Response(r.content, status=r.status_code, content_type=r.headers.get('content-type','application/octet-stream'))
    except Exception as e:
        return jsonify({"error": str(e)}), 502

@app.route('/api/collect', methods=['POST'])
def api_collect():
    body = request.get_json(silent=True) or {}
    source = body.get("source")
    term = (body.get("term") or body.get("q") or "").strip()
    limit = int(body.get("limit") or 10)
    if not source or not term:
        return jsonify({"error":"missing source or term"}), 400

    try:
        if source == "suggest":
            url = f"https://suggestqueries.google.com/complete/search?client=firefox&hl=en&q={requests.utils.requote_uri(term)}"
            r = safe_get(url)
            return Response(r.content, status=r.status_code, content_type="application/json")
        elif source in ["itunes", "appstore"]:
            url = f"https://itunes.apple.com/search?term={requests.utils.requote_uri(term)}&entity=software&limit={limit}"
            r = safe_get(url)
            return Response(r.content, status=r.status_code, content_type="application/json")
        elif source == "wiki":
            url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={requests.utils.requote_uri(term)}&format=json"
            r = safe_get(url)
            return Response(r.content, status=r.status_code, content_type="application/json")
        else:
            return jsonify({"error":"unknown source"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
