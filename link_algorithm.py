# link_algorithm.py
# Thuật toán khử mơ hồ và liên kết dữ liệu local với DBpedia thật.

from difflib import SequenceMatcher


def similarity(a, b):
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()


def keyword_bonus(local_field, dbpedia_record):
    """Bổ sung điểm nếu researchArea xuất hiện trong field raw hoặc abstract của DBpedia."""
    local = str(local_field).lower()
    text = " ".join([
        str(dbpedia_record.get("field", "")),
        str(dbpedia_record.get("dbpedia_field_raw", "")),
        str(dbpedia_record.get("abstract", ""))
    ]).lower()

    keyword_groups = {
        "computer science": ["computer", "computing", "programming", "algorithm", "artificial intelligence"],
        "artificial intelligence": ["artificial intelligence", "ai", "computer science"],
        "information theory": ["information theory", "communication theory"],
        "economics": ["economics", "economist", "economic"],
        "medicine": ["medicine", "medical", "physician", "doctor"],
        "microbiology": ["microbiology", "microbiologist", "bacteriology"],
        "pharmacology": ["pharmacology", "medicine", "artemisinin", "malaria"]
    }

    keywords = keyword_groups.get(local, [local])
    return 1.0 if any(k in text for k in keywords) else 0.0


def compute_matching_score(local_record, dbpedia_record):
    """
    Tính điểm khớp giữa local researcher và DBpedia record.
    Trọng số:
    - Tên: 45 điểm
    - Đơn vị công tác: 25 điểm
    - Lĩnh vực nghiên cứu: 30 điểm
    """
    score = 0.0

    name_score = similarity(local_record.get("name", ""), dbpedia_record.get("name", ""))
    score += name_score * 45

    affil_local = local_record.get("affiliation", "")
    univ_local = local_record.get("university", "")
    affil_dbpedia = dbpedia_record.get("affiliation", "")
    raw_affil_dbpedia = dbpedia_record.get("dbpedia_affiliation_raw", "")

    affil_score = max(
        similarity(affil_local, affil_dbpedia),
        similarity(univ_local, affil_dbpedia),
        similarity(affil_local, raw_affil_dbpedia),
        similarity(univ_local, raw_affil_dbpedia)
    )
    score += affil_score * 25

    field_local = local_record.get("researchArea", "")
    field_dbpedia = dbpedia_record.get("field", "")
    raw_field_dbpedia = dbpedia_record.get("dbpedia_field_raw", "")

    field_score = max(
        similarity(field_local, field_dbpedia),
        similarity(field_local, raw_field_dbpedia),
        keyword_bonus(field_local, dbpedia_record)
    )
    score += field_score * 30

    return round(score, 2)


def disambiguate_and_link(local_records, dbpedia_records, threshold=50.0):
    results = []

    for local in local_records:
        best_match = None
        best_score = 0.0

        for dbpedia in dbpedia_records:
            score = compute_matching_score(local, dbpedia)
            if score > best_score:
                best_score = score
                best_match = dbpedia

        if best_score >= threshold and best_match:
            result = {
                "researcher_id": local["researcher_id"],
                "local_name": local["name"],
                "dbpedia_uri": best_match["@id"],
                "dbpedia_name": best_match["name"],
                "score": best_score,
                "status": "linked"
            }
        else:
            result = {
                "researcher_id": local["researcher_id"],
                "local_name": local["name"],
                "dbpedia_uri": None,
                "dbpedia_name": None,
                "score": best_score,
                "status": "unlinked"
            }

        results.append(result)
        print(f"  {'✅' if result['status'] == 'linked' else '❌'} "
              f"{local['name']} → {result.get('dbpedia_uri', 'Không tìm thấy')} "
              f"(điểm: {best_score})")

    return results
