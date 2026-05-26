# simulate_failure.py - sửa lỗi venv

import subprocess
import time
import requests
import threading
import sys  # ← thêm dòng này

def wait_for_node(url, timeout=15):
    for _ in range(timeout):
        try:
            requests.get(f"{url}/health", timeout=1)
            return True
        except:
            time.sleep(1)
    return False

print("⚠️  Hãy tắt hết 3 terminal node cũ trước khi chạy!")
print("Nhấn Enter để tiếp tục...")
input()

print("🚀 Khởi động 3 nút mới...")

# ↓ Dùng sys.executable thay vì "python"
proc_a = subprocess.Popen([sys.executable, "nodes/node_a.py"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
proc_b = subprocess.Popen([sys.executable, "nodes/node_b.py"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
proc_c = subprocess.Popen([sys.executable, "nodes/node_c.py"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print("⏳ Đang chờ các nút khởi động...")
wait_for_node("http://localhost:5001")
wait_for_node("http://localhost:5002")
wait_for_node("http://localhost:5003")
print("✅ Cả 3 nút đang chạy!")

print("\n⚡ Bắt đầu liên kết dữ liệu...")
print("⚠️  Sau 5 giây, Node B sẽ bị ngắt đột ngột!")

def kill_node_b():
    time.sleep(5)
    print("\n💀 [GIẢ LẬP LỖI] Đang ngắt Node B...")
    proc_b.terminate()
    proc_b.wait()
    print("💀 Node B đã bị ngắt hoàn toàn!")

killer = threading.Thread(target=kill_node_b)
killer.start()

from master import run_all_nodes
from visualize import visualize_knowledge_graph
results = run_all_nodes()
visualize_knowledge_graph(results)

proc_a.terminate()
proc_c.terminate()
print("\n✅ Demo hoàn tất!")