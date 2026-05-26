# visualize.py
# Vẽ Knowledge Graph gọn hơn: chia thành 2 dãy, node nhỏ hơn

import math
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def shorten_uri(uri):
    """Chuyển URI DBpedia thành tên ngắn gọn để hiển thị"""
    if not uri:
        return "Unlinked"
    return uri.split("/")[-1].replace("_", " ")


def visualize_knowledge_graph(results_log):
    G = nx.Graph()
    local_nodes = []
    dbpedia_nodes = []
    edge_labels = {}
    pos = {}

    pairs = []

    # Gom tất cả các liên kết thành danh sách
    for node_id in sorted(results_log.keys()):
        log = results_log[node_id]

        if log["status"] != "success":
            continue

        for record in log.get("details", []):
            if record["status"] != "linked":
                continue

            local_label = (
                f"LOCAL\n{record['researcher_id']}\n"
                f"{record['local_name']}\n"
                f"Node {node_id}"
            )

            dbpedia_label = f"DBpedia\n{shorten_uri(record['dbpedia_uri'])}"

            pairs.append((local_label, dbpedia_label, record["score"]))

    total = len(pairs)
    if total == 0:
        print("❌ Không có dữ liệu để vẽ graph.")
        return

    # Chia thành 2 dãy
    split_index = math.ceil(total / 2)
    row1 = pairs[:split_index]
    row2 = pairs[split_index:]

    # Vị trí:
    # Dãy 1: local x=0, dbpedia x=4
    # Dãy 2: local x=8, dbpedia x=12
    def place_row(row_pairs, x_local, x_dbpedia):
        for i, (local_label, dbpedia_label, score) in enumerate(row_pairs):
            y = len(row_pairs) - i

            G.add_node(local_label, type="local")
            G.add_node(dbpedia_label, type="dbpedia")
            G.add_edge(local_label, dbpedia_label)

            local_nodes.append(local_label)
            dbpedia_nodes.append(dbpedia_label)

            pos[local_label] = (x_local, y)
            pos[dbpedia_label] = (x_dbpedia, y)

            edge_labels[(local_label, dbpedia_label)] = f"{score:.0f}đ"

    place_row(row1, 0, 4)
    place_row(row2, 8, 12)

    plt.figure(figsize=(18, 9))
    plt.title(
        "Knowledge Graph – Liên kết dữ liệu cục bộ với DBpedia",
        fontsize=18,
        fontweight="bold",
        pad=20
    )

    # Vẽ node Local
    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=local_nodes,
        node_color="#4A90D9",
        node_size=4600,
        alpha=0.95
    )

    # Vẽ node DBpedia
    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=dbpedia_nodes,
        node_color="#E05252",
        node_size=4600,
        alpha=0.95
    )

    # Vẽ cạnh
    nx.draw_networkx_edges(
        G,
        pos,
        width=1.8,
        alpha=0.55,
        edge_color="#666666"
    )

    # Nhãn cạnh
    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_size=8,
        font_color="#333333",
        label_pos=0.5
    )

    # Nhãn node
    nx.draw_networkx_labels(
        G,
        pos,
        font_size=8,
        font_color="black",
        font_weight="bold"
    )

    # Chú thích
    blue_patch = mpatches.Patch(color="#4A90D9", label="Dữ liệu cục bộ (Local)")
    red_patch = mpatches.Patch(color="#E05252", label="Dữ liệu DBpedia (Global)")

    plt.legend(
        handles=[blue_patch, red_patch],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.04),
        ncol=2,
        fontsize=12
    )

    plt.axis("off")
    plt.tight_layout()
    plt.savefig("knowledge_graph.png", dpi=200, bbox_inches="tight")
    plt.show()

    print("✅ Đã lưu: knowledge_graph.png")


if __name__ == "__main__":
    print("Vui lòng chạy master.py để tạo kết quả liên kết và vẽ graph.")