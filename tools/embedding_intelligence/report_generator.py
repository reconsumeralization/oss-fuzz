#!/usr/bin/env python3
import os
import json
from pathlib import Path
from typing import List, Dict, Any

# Protobuf reader optional
try:
	from . import gtm_pb2  # type: ignore
	_PROTO = True
except Exception:
	_PROTO = False


def _read_event_file(path: Path) -> Dict[str, Any]:
	if path.suffix == '.json':
		try:
			return json.loads(path.read_text(encoding='utf-8', errors='ignore'))
		except Exception:
			return {}
	elif path.suffix == '.pb' and _PROTO:
		try:
			evt = gtm_pb2.EmbeddingEvent()
			data = path.read_bytes()
			evt.ParseFromString(data)
			return {k.name: getattr(evt, k.name) for k in evt.DESCRIPTOR.fields}
		except Exception:
			return {}
	return {}


def load_events(cache_dir: str) -> List[Dict[str, Any]]:
	events_dir = Path(cache_dir) / 'gtm_events'
	if not events_dir.exists():
		return []
	items: List[Dict[str, Any]] = []
	for p in sorted(events_dir.glob('*.*')):
		if item := _read_event_file(p):
			items.append(item)
	return items


def generate_html_report(events: List[Dict[str, Any]]) -> str:
	total = len(events)
	emb_used = sum(1 for e in events if e.get('embedding_used'))
	cache_hits = sum(1 for e in events if e.get('cache_hit'))
	novel = sum(1 for e in events if e.get('is_novel'))
	dup = sum(bool(e.get('is_duplicate'))
	total_cost = sum(float(e.get('estimated_cost', 0.0)) for e in events)
	
	rows = []
	for e in events[-200:]:
		rows.append(
			f"<tr><td>{e.get('timestamp_ms','')}</td><td>{e.get('project_name','')}</td>"
			f"<td>{e.get('crash_type','')}</td><td>{e.get('priority_score','')}</td>"
			f"<td>{'yes' if e.get('embedding_used') else 'no'}</td><td>{'yes' if e.get('cache_hit') else 'no'}</td>"
			f"<td>{e.get('estimated_cost','')}</td><td>{e.get('decision_reason','')}</td></tr>"
		)
	
	html = f"""
<!doctype html>
<html><head><meta charset='utf-8'><title>Embedding Intelligence Report</title>
<style>
body{{font-family:Arial, sans-serif; margin:20px;}}
.kpi{{display:flex; gap:20px; margin-bottom:20px;}}
.kpi div{{background:#f6f6f6; padding:12px 16px; border-radius:8px;}}
.table{{border-collapse:collapse; width:100%;}}
.table th,.table td{{border:1px solid #ddd; padding:8px; font-size:13px;}}
.table th{{background:#fafafa; text-align:left;}}
</style></head>
<body>
<h2>OSS-Fuzz Embedding Intelligence - Local Report</h2>
<div class="kpi">
	<div><b>Total events</b><br>{total}</div>
	<div><b>Embedding used</b><br>{emb_used}</div>
	<div><b>Cache hits</b><br>{cache_hits}</div>
	<div><b>Novel</b><br>{novel}</div>
	<div><b>Duplicates</b><br>{dup}</div>
	<div><b>Total cost ($)</b><br>{total_cost:.4f}</div>
</div>
<table class="table">
	<thead><tr><th>Time</th><th>Project</th><th>Crash</th><th>Priority</th><th>Embed?</th><th>Cache?</th><th>Cost</th><th>Reason</th></tr></thead>
	<tbody>
		{''.join(rows)}
	</tbody>
</table>
</body></html>
"""
	return html


def write_report(cache_dir: str, out_path: str) -> str:
	events = load_events(cache_dir)
	html = generate_html_report(events)
	Path(out_path).write_text(html, encoding='utf-8')
	return out_path