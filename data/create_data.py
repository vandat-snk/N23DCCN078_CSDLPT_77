# data/create_data.py
# Tạo dữ liệu local University Research cho 3 node phân tán.
# @id ban đầu là None/null; sau khi chạy master.py, hệ thống sẽ cập nhật @id bằng URI thật lấy từ DBpedia.

import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONTEXT = {
    "name": "http://xmlns.com/foaf/0.1/name",
    "affiliation": "http://dbpedia.org/ontology/affiliation",
    "researchArea": "http://dbpedia.org/ontology/field",
    "university": "http://dbpedia.org/ontology/university",
    "publications": "http://dbpedia.org/ontology/publication"
}

def researcher(researcher_id, name, affiliation, research_area, university, publications):
    return {
        "@context": CONTEXT,
        "@id": None,
        "researcher_id": researcher_id,
        "name": name,
        "affiliation": affiliation,
        "researchArea": research_area,
        "university": university,
        "publications": publications
    }

researchers_cntt = [
    researcher("LOCAL-001", "Alan Turing", "University of Manchester", "Computer Science", "Manchester", 20),
    researcher("LOCAL-002", "Tim Berners-Lee", "Massachusetts Institute of Technology", "Computer Science", "MIT", 18),
    researcher("LOCAL-003", "Donald Knuth", "Stanford University", "Computer Science", "Stanford", 30),
    researcher("LOCAL-004", "Edsger W. Dijkstra", "Eindhoven University of Technology", "Computer Science", "TU/e", 22),
    researcher("LOCAL-005", "Ada Lovelace", "University of London", "Computer Science", "London", 8),
    researcher("LOCAL-006", "Claude Shannon", "Massachusetts Institute of Technology", "Information Theory", "MIT", 25),
    researcher("LOCAL-007", "John McCarthy", "Stanford University", "Artificial Intelligence", "Stanford", 19),
    researcher("LOCAL-008", "Võ Van Dat", "PTIT", "Distributed Databases", "PTIT", 3),
]

researchers_kinh_te = [
    researcher("LOCAL-051", "Adam Smith", "University of Glasgow", "Economics", "Glasgow", 12),
    researcher("LOCAL-052", "John Maynard Keynes", "University of Cambridge", "Economics", "Cambridge", 18),
    researcher("LOCAL-053", "Milton Friedman", "University of Chicago", "Economics", "Chicago", 25),
    researcher("LOCAL-054", "Amartya Sen", "Harvard University", "Economics", "Harvard", 21),
    researcher("LOCAL-055", "Joseph Stiglitz", "Columbia University", "Economics", "Columbia", 24),
]

researchers_y_te = [
    researcher("LOCAL-101", "Louis Pasteur", "University of Strasbourg", "Microbiology", "Strasbourg", 20),
    researcher("LOCAL-102", "Alexander Fleming", "St Mary's Hospital Medical School", "Medicine", "St Mary's", 15),
    researcher("LOCAL-103", "Jonas Salk", "University of Pittsburgh", "Medicine", "Pittsburgh", 12),
    researcher("LOCAL-104", "Tu Youyou", "China Academy of Chinese Medical Sciences", "Pharmacology", "CACMS", 16),
    researcher("LOCAL-105", "Hoang Phu Huy", "Local Medical University", "Nursing", "LMU", 2),
]

def save_json(filename, data):
    path = os.path.join(BASE_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Đã tạo {filename}: {len(data)} bản ghi")

save_json("node_a_cntt.json", researchers_cntt)
save_json("node_b_kinh_te.json", researchers_kinh_te)
save_json("node_c_y_te.json", researchers_y_te)

print("✅ Hoàn tất tạo dữ liệu local. Các bản ghi local có @id = null.")
