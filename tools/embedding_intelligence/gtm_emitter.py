#!/usr/bin/env python3
import time
import uuid
import json
from pathlib import Path
from typing import Dict, Optional

try:
    # gtm_pb2 will be generated into the same package directory
    from . import gtm_pb2
    _PROTO_AVAILABLE = True
except Exception:
    try:
        import gtm_pb2  # type: ignore
        _PROTO_AVAILABLE = True
    except Exception:
        _PROTO_AVAILABLE = False


def _build_event_dict(project_name: Optional[str], crash_report: Dict, analysis: Dict, model_name: str) -> Dict:
    stats = analysis.get("intelligence_stats", {})
    cluster = analysis.get("cluster_analysis", {})
    reasons = []
    if float(analysis.get("priority_score", 0.0)) > 0.8:
        reasons.append("high_priority")
    if float(analysis.get("exploit_risk_score", 0.0)) > 0.7:
        reasons.append("high_risk")
    if bool(cluster.get("is_novel", False)):
        reasons.append("novel_cluster")
    if not analysis.get("vulnerability_matches"):
        reasons.append("no_known_patterns")

    return {
        "event_id": str(uuid.uuid4()),
        "timestamp_ms": int(time.time() * 1000),
        "project_name": project_name or "",
        "crash_signature": analysis.get("crash_signature", ""),
        "crash_type": analysis.get("crash_type", crash_report.get("crash_type", "")),
        "embedding_used": bool(analysis.get("embedding_analysis_used", False)),
        "cache_hit": bool(analysis.get("cache_hit", False)),
        "estimated_cost": float(analysis.get("estimated_cost", 0.0)),
        "processing_time_seconds": float(stats.get("processing_time_seconds", 0.0)),
        "model": model_name or "",
        "source": "oss-fuzz",
        "version": "1.0",
        "decision_reason": ",".join(reasons),
        "priority_score": float(analysis.get("priority_score", 0.0)),
        "exploit_risk_score": float(analysis.get("exploit_risk_score", 0.0)),
        "is_novel": bool(cluster.get("is_novel", False)),
        "is_duplicate": bool(cluster.get("is_duplicate", False)),
    }


def emit_embedding_event(
    project_name: Optional[str],
    crash_report: Dict,
    analysis: Dict,
    config: Dict,
    model_name: str = "models/embedding-001",
) -> Optional[Path]:
    """Emit a GTM protobuf record capturing embedding analysis telemetry.

    Returns the path to the written .pb (or JSON fallback) file, or None if emission is skipped.
    """
    # Output path under cache dir
    cache_dir = Path(config.get("cache_dir", "/tmp/oss_fuzz_embeddings"))
    out_dir = cache_dir / "gtm_events"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build canonical event dict first
    event_dict = _build_event_dict(project_name, crash_report, analysis, model_name)

    if _PROTO_AVAILABLE:
        try:
            # Map dict to protobuf
            if hasattr(gtm_pb2, "EmbeddingEvent"):
                event = gtm_pb2.EmbeddingEvent()
                for key, value in event_dict.items():
                    setattr(event, key, value)
                out_path = out_dir / f"{event.timestamp_ms}_{event.event_id}.pb"
                with open(out_path, "wb") as f:
                    f.write(event.SerializeToString())
                return out_path
        except Exception:
            pass

    # Fallback: JSON record if protobuf unavailable
    try:
        out_path = out_dir / f"{event_dict['timestamp_ms']}_{event_dict['event_id']}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(event_dict, f, ensure_ascii=False, separators=(",", ":"))
        return out_path
    except Exception:
        return None