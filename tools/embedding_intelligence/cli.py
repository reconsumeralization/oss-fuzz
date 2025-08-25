#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any

from .report_generator import load_events, write_report


def cmd_status(args: argparse.Namespace) -> int:
	cache_dir = args.cache_dir
	events = load_events(cache_dir)
	total = len(events)
	emb_used = sum(bool(e.get('embedding_used'))
	cache_hits = sum(1 for e in events if e.get('cache_hit'))
	print(f"Events: {total} | Embedding used: {emb_used} | Cache hits: {cache_hits}")
	return 0


def cmd_events(args: argparse.Namespace) -> int:
	cache_dir = args.cache_dir
	events = load_events(cache_dir)
	print(json.dumps(events[-args.tail:], indent=2))
	return 0


def cmd_report(args: argparse.Namespace) -> int:
	cache_dir = args.cache_dir
	out = args.out
	path = write_report(cache_dir, out)
	print(f"Report written: {path}")
	return 0


def main() -> int:
	p = argparse.ArgumentParser(description='Embedding Intelligence CLI (local-only)')
	sub = p.add_subparsers(dest='cmd', required=True)

	p.add_argument('--cache-dir', default='/tmp/oss_fuzz_embeddings', help='Base cache dir')

	p_status = sub.add_parser('status', help='Show basic counters')
	p_status.set_defaults(func=cmd_status)

	p_events = sub.add_parser('events', help='Print recent events')
	p_events.add_argument('--tail', type=int, default=10, help='Number of events to show')
	p_events.set_defaults(func=cmd_events)

	p_report = sub.add_parser('report', help='Generate HTML report')
	p_report.add_argument('--out', default='embedding_report.html', help='Output HTML path')
	p_report.set_defaults(func=cmd_report)

	args = p.parse_args()
	return int(args.func(args) or 0)


if __name__ == '__main__':
	raise SystemExit(main())