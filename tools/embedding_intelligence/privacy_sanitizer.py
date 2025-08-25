#!/usr/bin/env python3
import re
from typing import Dict, Any

_HEX_ADDR = re.compile(r'0x[0-9a-fA-F]+')
_PATH_LIKE = re.compile(r'(?:^|\s)(/[^\s:]+)+')
_LINE_NUM = re.compile(r':\d+')
_NUMBERS = re.compile(r'\b\d{4,}\b')

def sanitize_text(value: str) -> str:
	if not value:
		return value
	v = value
	v = _HEX_ADDR.sub('ADDR', v)
	v = _LINE_NUM.sub(':LINE', v)
	v = _PATH_LIKE.sub(' /PATH ', v)
	v = _NUMBERS.sub('NUM', v)
	return v[:2000]

def sanitize_event_dict(event: Dict[str, Any]) -> Dict[str, Any]:
	return {
		k: sanitize_text(v) if isinstance(v, str) else v for k, v in event.items()
	}