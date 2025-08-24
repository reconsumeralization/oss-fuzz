#!/usr/bin/env python3
import json
from pathlib import Path
import os
import sys

# Ensure local import
sys.path.insert(0, str(Path(__file__).parent))

from lean_crash_analyzer import LeanEmbeddingIntelligence


def main():
	os.environ.setdefault('ENABLE_EMBEDDING_INTELLIGENCE', 'true')
	config = {
		'cache_dir': str(Path.cwd() / 'tmp_embeddings_demo'),
		'project_name': 'demo'
	}
	an = LeanEmbeddingIntelligence(config)
	crash = {
		'crash_type': 'heap-buffer-overflow',
		'error_message': 'AddressSanitizer: heap-buffer-overflow on address 0x60200000eff0',
		'stack_trace': '#0 0x4f5e35 in main /src/test.c:42:5',
		'input_info': {'size': 256, 'type': 'binary'}
	}
	res = an.analyze_crash_intelligently(crash)
	print(json.dumps(res, indent=2, default=str))
	print('Telemetry dir:', Path(config['cache_dir']) / 'gtm_events')


if __name__ == '__main__':
	main()