# master.py
# Chạy toàn bộ hệ thống: đọc DBpedia thật đã fetch, lấy dữ liệu từ node,
# khử mơ hồ, cập nhật @id và vẽ Knowledge Graph.

import os
import json
import time
import threading
import requests
from link_algorithm import disambiguate_and_link

NODES = {
    "A": "http://localhost:5001",
    "B": "http://localhost:5002",
    "C": "http://localhost:5003"
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DBPEDIA_FILE = os.path.join(BASE_DIR, "data", "dbpedia_snippets.json")


def check_node_alive(node_id, url):
    try:
        resp = requests.get(f"{url}/health", timeout=2)
        return resp.status_code == 200
    except Exception:
        return False


def load_dbpedia_records():
    if not os.path.exists(DBPEDIA_FILE):
        raise FileNotFoundError(
            "Không tìm thấy data/dbpedia_snippets.json. "
            "Hãy chạy: python data/create_dbpedia.py"
        )

    with open(DBPEDIA_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)

    print(f"📚 Đã tải {len(records)} bản ghi DBpedia từ {DBPEDIA_FILE}")
    return records


def process_node(node_id, url, dbpedia_records, results_log):
    print(f"\n{'=' * 40}")
    print(f"🔄 Bắt đầu xử lý Node {node_id}...")

    try:
        if not check_node_alive(node_id, url):
            print(f"❌ Node {node_id} KHÔNG PHẢN HỒI! Bỏ qua node này.")
            results_log[node_id] = {"status": "failed", "reason": "Node offline"}
            return

        resp = requests.get(f"{url}/data", timeout=5)
        resp.raise_for_status()
        local_records = resp.json()["data"]
        print(f"📦 Node {node_id}: Nhận được {len(local_records)} bản ghi")

        link_results = disambiguate_and_link(local_records, dbpedia_records)

        linked_count = 0
        for result in link_results:
            if result["status"] == "linked":
                update_resp = requests.post(
                    f"{url}/update_link",
                    json={
                        "researcher_id": result["researcher_id"],
                        "dbpedia_uri": result["dbpedia_uri"]
                    },
                    timeout=5
                )
                update_resp.raise_for_status()
                linked_count += 1

        total = len(link_results)
        accuracy = (linked_count / total * 100) if total > 0 else 0

        results_log[node_id] = {
            "status": "success",
            "total": total,
            "linked": linked_count,
            "accuracy": round(accuracy, 1),
            "details": link_results
        }
        print(f"✅ Node {node_id} hoàn thành: {linked_count}/{total} liên kết ({accuracy:.1f}%)")

    except Exception as e:
        print(f"❌ Node {node_id} lỗi trong quá trình xử lý: {e}")
        results_log[node_id] = {"status": "failed", "reason": str(e)}


def run_all_nodes():
    dbpedia_records = load_dbpedia_records()

    results_log = {}
    threads = []
    start_time = time.time()

    for node_id, url in NODES.items():
        t = threading.Thread(target=process_node, args=(node_id, url, dbpedia_records, results_log))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    elapsed = time.time() - start_time

    print("\n" + "=" * 50)
    print("📊 BÁO CÁO TỔNG KẾT")
    print("=" * 50)

    total_records = 0
    total_linked = 0

    for node_id in sorted(results_log.keys()):
        log = results_log[node_id]
        if log["status"] == "success":
            total_records += log["total"]
            total_linked += log["linked"]
            print(f"  Node {node_id}: {log['linked']}/{log['total']} ({log['accuracy']}%)")
        else:
            print(f"  Node {node_id}: ❌ LỖI - {log['reason']}")

    overall_accuracy = (total_linked / total_records * 100) if total_records > 0 else 0
    print(f"\n  🎯 Tổng Linkage Accuracy: {overall_accuracy:.1f}%")
    print(f"  ⏱️  Thời gian thực thi: {elapsed * 1000:.0f}ms")

    return results_log


if __name__ == "__main__":
    from visualize import visualize_knowledge_graph
    results = run_all_nodes()
    visualize_knowledge_graph(results)
