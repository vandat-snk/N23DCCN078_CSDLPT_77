# nodes/node_b.py - Node B: Dữ liệu Kinh tế (cổng 5002)

from flask import Flask, jsonify, request
import json, os

app = Flask(__name__)
NODE_ID = "B"
PORT = 5002
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "node_b_kinh_te.json")

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route("/data", methods=["GET"])
def get_data():
    data = load_data()
    return jsonify({"node": NODE_ID, "count": len(data), "data": data})

@app.route("/update_link", methods=["POST"])
def update_link():
    payload = request.json
    researcher_id = payload["researcher_id"]
    dbpedia_uri = payload["dbpedia_uri"]
    data = load_data()
    for record in data:
        if record["researcher_id"] == researcher_id:
            record["@id"] = dbpedia_uri
            save_data(data)
            return jsonify({"status": "success", "message": f"Đã liên kết {researcher_id}"})
    return jsonify({"status": "error", "message": "Không tìm thấy ID"}), 404

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"node": NODE_ID, "status": "alive"})

if __name__ == "__main__":
    print(f"🟢 Node {NODE_ID} (Kinh tế) đang chạy trên cổng {PORT}...")
    app.run(port=PORT, debug=False)
