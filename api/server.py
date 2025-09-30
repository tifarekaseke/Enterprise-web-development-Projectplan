# api/server.py
from http.server import BaseHTTPRequestHandler, HTTPServer # simple http server to help us focus on API logic without external deps (django, flask, fastapi, etc)
from urllib.parse import urlparse # parse URL paths and query params ( no external deps )
import json, base64, os, time # stdlib only
from typing import Dict, Any, List
from dsa.parse_xml import parse_momo_xml

# ====== Config ======
HOST = "127.0.0.1"
PORT = 8008
XML_PATH = os.environ.get("MOMO_XML", "modified_sms_v2.xml")

# Basic Auth credentials (for demo; DO NOT hardcode in production)
BASIC_USER = os.environ.get("API_USER", "admin")
BASIC_PASS = os.environ.get("API_PASS", "admin123")

# ====== In-memory store ======
# We keep two structures for DSA comparison and fast lookups:
#   - transactions_list: list of dicts
#   - transactions_index: dict[id] = dict
transactions_list: List[Dict[str, Any]] = []
transactions_index: Dict[int, Dict[str, Any]] = {}
next_id = 1

def load_data():
    global transactions_list, transactions_index, next_id
    if os.path.exists(XML_PATH):
        transactions_list = parse_momo_xml(XML_PATH)
    else:
        transactions_list = []
    transactions_index = {int(t["id"]): t for t in transactions_list}
    next_id = (max(transactions_index.keys()) + 1) if transactions_index else 1

def ensure_auth(handler: BaseHTTPRequestHandler) -> bool:
    auth = handler.headers.get("Authorization")
    if not auth or not auth.startswith("Basic "):
        handler.send_response(401)
        handler.send_header("WWW-Authenticate", 'Basic realm="momo"')
        handler.end_headers()
        handler.wfile.write(b'{"error":"Unauthorized"}')
        return False

    try:
        b64 = auth.split(" ", 1)[1]
        decoded = base64.b64decode(b64).decode("utf-8")
        user, pwd = decoded.split(":", 1)
    except Exception:
        handler.send_response(401)
        handler.send_header("WWW-Authenticate", 'Basic realm="momo"')
        handler.end_headers()
        handler.wfile.write(b'{"error":"Unauthorized"}')
        return False

    if user == BASIC_USER and pwd == BASIC_PASS:
        return True
    handler.send_response(401)
    handler.send_header("WWW-Authenticate", 'Basic realm="momo"')
    handler.end_headers()
    handler.wfile.write(b'{"error":"Unauthorized"}')
    return False

def read_body_json(handler: BaseHTTPRequestHandler):
    length = int(handler.headers.get("Content-Length", "0"))
    raw = handler.rfile.read(length) if length > 0 else b""
    if not raw:
        return None
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return None

class App(BaseHTTPRequestHandler): # our main API handler class (extends BaseHTTPRequestHandler) for CRUD operations
    def _send_json(self, obj, status=200):
        payload = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    # CRUD Handlers
    def do_GET(self):
        if not ensure_auth(self):
            return
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]
        # /transactions
        if parts == ["transactions"]:
            self._send_json(transactions_list)
            return
        # /transactions/{id}
        if len(parts) == 2 and parts[0] == "transactions":
            try:
                tx_id = int(parts[1])
            except ValueError:
                self._send_json({"error": "invalid id"}, 400)
                return
            tx = transactions_index.get(tx_id)
            if not tx:
                self._send_json({"error": "not found"}, 404)
                return
            self._send_json(tx)
            return
        self._send_json({"error": "unknown endpoint"}, 404)

    def do_POST(self):
        if not ensure_auth(self):
            return
        parsed = urlparse(self.path)
        if parsed.path != "/transactions":
            self._send_json({"error": "unknown endpoint"}, 404)
            return
        body = read_body_json(self)
        if not body:
            self._send_json({"error": "invalid json"}, 400)
            return
        required = ["type", "amount", "currency", "sender", "receiver", "timestamp"]
        if any(k not in body for k in required):
            self._send_json({"error": f"missing fields, required={required}"}, 400)
            return
        global next_id
        tx = {
            "id": next_id,
            "type": body["type"],
            "amount": float(body["amount"]),
            "currency": body.get("currency", "RWF"),
            "sender": body["sender"],
            "receiver": body["receiver"],
            "timestamp": body["timestamp"],
            "raw_text": body.get("raw_text", ""),
        }
        transactions_list.append(tx)
        transactions_index[tx["id"]] = tx
        next_id += 1
        self._send_json(tx, 201)

    def do_PUT(self):
        if not ensure_auth(self):
            return
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) != 2 or parts[0] != "transactions":
            self._send_json({"error": "unknown endpoint"}, 404)
            return
        try:
            tx_id = int(parts[1])
        except ValueError:
            self._send_json({"error": "invalid id"}, 400)
            return
        existing = transactions_index.get(tx_id)
        if not existing:
            self._send_json({"error": "not found"}, 404)
            return
        body = read_body_json(self)
        if not body:
            self._send_json({"error": "invalid json"}, 400)
            return
        # Patch allowed fields
        for k in ["type", "amount", "currency", "sender", "receiver", "timestamp", "raw_text"]:
            if k in body:
                existing[k] = body[k] if k != "amount" else float(body[k])
        self._send_json(existing)

    def do_DELETE(self):
        if not ensure_auth(self):
            return
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) != 2 or parts[0] != "transactions":
            self._send_json({"error": "unknown endpoint"}, 404)
            return
        try:
            tx_id = int(parts[1])
        except ValueError:
            self._send_json({"error": "invalid id"}, 400)
            return
        if tx_id not in transactions_index:
            self._send_json({"error": "not found"}, 404)
            return
        # delete from dict + list
        tx = transactions_index.pop(tx_id)
        for i, row in enumerate(transactions_list):
            if row["id"] == tx_id:
                transactions_list.pop(i)
                break
        self._send_json({"status": "deleted", "id": tx_id})

def main():
    load_data()
    print(f"[boot] loaded {len(transactions_list)} transactions from {XML_PATH}")
    srv = HTTPServer((HOST, PORT), App)
    print(f"[listen] http://{HOST}:{PORT}  (Basic Auth user={BASIC_USER})")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n[shutdown]")
        srv.server_close()

if __name__ == "__main__":
    main()
