import os
import json
from typing import Dict, Any
from .gemini_client import generate_text_report
from datetime import datetime
from collections import Counter, defaultdict

STORAGE_DIR = os.getenv("STORAGE_DIR", "./storage")
REPORTS_DIR = os.path.join(STORAGE_DIR, "reports")
PUBLISHED_DIR = os.path.join(STORAGE_DIR, "published")
DATA_INDEX = os.path.join(STORAGE_DIR, "index.json")

os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(PUBLISHED_DIR, exist_ok=True)

# Simple index to map report_id -> file
try:
    if os.path.exists(DATA_INDEX):
        with open(DATA_INDEX, 'r', encoding='utf-8') as f:
            INDEX = json.load(f)
    else:
        INDEX = {}
except Exception:
    INDEX = {}


def _save_index():
    with open(DATA_INDEX, 'w', encoding='utf-8') as f:
        json.dump(INDEX, f, ensure_ascii=False, indent=2)


def aggregate_samples(samples):
    total = len(samples)
    counts_by_event = Counter()
    confidences = defaultdict(list)
    flags_counter = Counter()
    keywords_counter = Counter()

    for s in samples:
        det = s.get('detection', {})
        event = det.get('event_type') or det.get('event') or 'unknown'
        counts_by_event[event] += 1
        conf = det.get('confidence') or det.get('confidence_score')
        if isinstance(conf, (int, float)):
            confidences[event].append(float(conf))
        for f in det.get('flags', []) or []:
            flags_counter[f] += 1
        for k in det.get('keywords', []) or []:
            keywords_counter[k.lower()] += 1

    avg_confidence = {e: (sum(vals) / len(vals)) if vals else None for e, vals in confidences.items()}

    agg = {
        'total_samples': total,
        'counts_by_event': dict(counts_by_event),
        'avg_confidence_by_event': avg_confidence,
        'flags': dict(flags_counter.most_common()),
        'top_keywords': keywords_counter.most_common(10)
    }
    return agg


def generate_prompt_for_detection(sample_id, detection, agg=None):
    data = {
        'sample_id': sample_id,
        'detection': detection,
        'aggregated': agg
    }
    prompt = "Genera un reporte ejecutivo y técnico a partir de la siguiente detección y métricas agregadas:\n"
    prompt += json.dumps(data, ensure_ascii=False, indent=2)
    prompt += "\n\nInstrucciones:\n1) Resumen ejecutivo 120-180 palabras.\n2) Hallazgos técnicos.\n3) Recomendaciones operativas.\n4) Lista de keywords detectadas."
    return prompt


def process_detection(sample_id: str, detection: Dict[str, Any]):
    # For now we treat single sample; in future accept batches
    agg = aggregate_samples([{"sample_id": sample_id, "detection": detection}])
    prompt = generate_prompt_for_detection(sample_id, detection, agg)

    report_text = generate_text_report(prompt)

    report_id = f"report-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{sample_id}"
    filename = f"{REPORTS_DIR}/{report_id}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report_text)

    INDEX[report_id] = {"file": filename, "created_at": datetime.utcnow().isoformat(), "sample_id": sample_id}
    _save_index()

    summary = {
        "aggregated": agg,
        "sample_id": sample_id
    }
    return report_id, summary, filename


def get_report_path(report_id: str):
    return INDEX.get(report_id, {}).get('file')


def publish_words_for_report(report_id: str, order_token: str = "chimera"):
    """Reads report, extracts words (simple heuristic), and writes published file if order_token matches."""
    meta = INDEX.get(report_id)
    if not meta:
        return None
    if order_token.lower() != "chimera":
        return None
    path = meta.get('file')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return None

    # naive extraction: top words that look like keywords
    words = []
    for w in ["disparo", "gunshot", "ballistic_impulse"]:
        if w in content.lower():
            words.append(w)
    if not words:
        return None

    os.makedirs(PUBLISHED_DIR, exist_ok=True)
    pubfile = f"{PUBLISHED_DIR}/published_{report_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
    payload = {
        "report_id": report_id,
        "timestamp": datetime.utcnow().isoformat(),
        "words": words
    }
    with open(pubfile, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return pubfile
