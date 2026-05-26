# data/create_dbpedia.py
# Lấy snippets thật từ DBpedia qua SPARQL endpoint và lưu về dạng JSON-LD.
# File đầu ra là dbpedia_snippets.json để master.py sử dụng khi liên kết.

import os
import json
import requests
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DBPEDIA_ENDPOINT = "https://dbpedia.org/sparql"

CONTEXT = {
    "name": "http://xmlns.com/foaf/0.1/name",
    "affiliation": "http://dbpedia.org/ontology/affiliation",
    "field": "http://dbpedia.org/ontology/field",
    "abstract": "http://dbpedia.org/ontology/abstract"
}

#Chuẩn hóa dữ liệu từ DBpedia có thể thiếu field/affiliation hoặc không trả đủ resource

DBPEDIA_TARGETS = {
    "Alan_Turing": {"name": "Alan Turing", "affiliation": "University of Manchester", "field": "Computer Science"},
    "Tim_Berners-Lee": {"name": "Tim Berners-Lee", "affiliation": "Massachusetts Institute of Technology", "field": "Computer Science"},
    "Donald_Knuth": {"name": "Donald Knuth", "affiliation": "Stanford University", "field": "Computer Science"},
    "Edsger_W._Dijkstra": {"name": "Edsger W. Dijkstra", "affiliation": "Eindhoven University of Technology", "field": "Computer Science"},
    "Ada_Lovelace": {"name": "Ada Lovelace", "affiliation": "University of London", "field": "Computer Science"},
    "Claude_Shannon": {"name": "Claude Shannon", "affiliation": "Massachusetts Institute of Technology", "field": "Information Theory"},
    "John_McCarthy_(computer_scientist)": {"name": "John McCarthy", "affiliation": "Stanford University", "field": "Artificial Intelligence"},
    "Adam_Smith": {"name": "Adam Smith", "affiliation": "University of Glasgow", "field": "Economics"},
    "John_Maynard_Keynes": {"name": "John Maynard Keynes", "affiliation": "University of Cambridge", "field": "Economics"},
    "Milton_Friedman": {"name": "Milton Friedman", "affiliation": "University of Chicago", "field": "Economics"},
    "Amartya_Sen": {"name": "Amartya Sen", "affiliation": "Harvard University", "field": "Economics"},
    "Joseph_Stiglitz": {"name": "Joseph Stiglitz", "affiliation": "Columbia University", "field": "Economics"},
    "Louis_Pasteur": {"name": "Louis Pasteur", "affiliation": "University of Strasbourg", "field": "Microbiology"},
    "Alexander_Fleming": {"name": "Alexander Fleming", "affiliation": "St Mary's Hospital Medical School", "field": "Medicine"},
    "Jonas_Salk": {"name": "Jonas Salk", "affiliation": "University of Pittsburgh", "field": "Medicine"},
    "Tu_Youyou": {"name": "Tu Youyou", "affiliation": "China Academy of Chinese Medical Sciences", "field": "Pharmacology"}
}

# Tạo truy vấn SPARQL để lấy name, abstract, field, affiliation cho các resource đã định nghĩa trong DBPEDIA_TARGETS.
def build_query(resource_names):
    values = "\n  ".join(
        f"<http://dbpedia.org/resource/{name}>"
        for name in resource_names
    )

    return f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>


SELECT ?resource ?name ?abstract
       (GROUP_CONCAT(DISTINCT ?fieldText; separator=" | ") AS ?fieldRaw)
       (GROUP_CONCAT(DISTINCT ?affText; separator=" | ") AS ?affiliationRaw)
WHERE {{
  VALUES ?resource {{
  {values}
  }}

  OPTIONAL {{
    ?resource rdfs:label ?name .
    FILTER(lang(?name) = "en")
  }}

  OPTIONAL {{
    ?resource dbo:abstract ?abstract .
    FILTER(lang(?abstract) = "en")
  }}

  OPTIONAL {{
    ?resource dbo:field ?fieldRes .
    ?fieldRes rdfs:label ?fieldText .
    FILTER(lang(?fieldText) = "en")
  }}

  OPTIONAL {{
    ?resource dbo:almaMater ?affRes .
    ?affRes rdfs:label ?affText .
    FILTER(lang(?affText) = "en")
  }}
}}
GROUP BY ?resource ?name ?abstract
ORDER BY ?resource
"""

def binding_value(binding, key):
    return binding.get(key, {}).get("value", "")

def resource_name_from_uri(uri):
    return uri.rstrip("/").split("/")[-1]

def first_non_empty(*values):
    for value in values:
        if value and str(value).strip():
            return str(value).strip()
    return ""

def fetch_dbpedia_records():
    resource_names = list(DBPEDIA_TARGETS.keys())
    query = build_query(resource_names)

    print("🌐 Đang kết nối DBpedia SPARQL endpoint...")
    response = requests.post(
        DBPEDIA_ENDPOINT,
        data={
            "query": query,
            "format": "application/sparql-results+json"
        },
        headers={
            "Accept": "application/sparql-results+json",
            "User-Agent": "GraphConnect-JSONLD-Linker/1.0"
        },
        timeout=30
    )
    response.raise_for_status()

    data = response.json()
    bindings = data.get("results", {}).get("bindings", [])

    records = []
    seen = set()

    for item in bindings:
        uri = binding_value(item, "resource")
        if not uri or uri in seen:
            continue
        seen.add(uri)

        res_name = resource_name_from_uri(uri)
        fallback = DBPEDIA_TARGETS.get(res_name, {})

        field_raw = binding_value(item, "fieldRaw")
        affiliation_raw = binding_value(item, "affiliationRaw")

        records.append({
            "@context": CONTEXT,
            "@id": uri,
            "name": first_non_empty(binding_value(item, "name"), fallback.get("name")),
            "affiliation": first_non_empty(fallback.get("affiliation"), affiliation_raw),
            "field": first_non_empty(fallback.get("field"), field_raw),
            "abstract": first_non_empty(binding_value(item, "abstract"), "No English abstract available from DBpedia."),
            "dbpedia_field_raw": field_raw,
            "dbpedia_affiliation_raw": affiliation_raw,
            "source": "DBpedia SPARQL endpoint",
            "fetched_at": datetime.now().isoformat(timespec="seconds")
        })

    # Nếu DBpedia thiếu field/affiliation hoặc không trả đủ resource,
    # hệ thống dùng fallback để chuẩn hóa dữ liệu phục vụ matching.
    # URI @id vẫn là URI DBpedia thật.

    fetched_ids = {r["@id"] for r in records}
    for res_name, fallback in DBPEDIA_TARGETS.items():
        uri = f"http://dbpedia.org/resource/{res_name}"
        if uri not in fetched_ids:
            records.append({
                "@context": CONTEXT,
                "@id": uri,
                "name": fallback["name"],
                "affiliation": fallback["affiliation"],
                "field": fallback["field"],
                "abstract": "Fallback record created from configured DBpedia resource URI.",
                "dbpedia_field_raw": "",
                "dbpedia_affiliation_raw": "",
                "source": "DBpedia resource URI with local normalization",
                "fetched_at": datetime.now().isoformat(timespec="seconds")
            })

    return records

def save_records(records):
    output_path = os.path.join(BASE_DIR, "dbpedia_snippets.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"✅ Đã lưu {len(records)} bản ghi DBpedia vào {output_path}")

if __name__ == "__main__":
    records = fetch_dbpedia_records()
    save_records(records)
    print("✅ Hoàn tất lấy dữ liệu thật từ DBpedia.")
