#!/usr/bin/env python3
"""
Intelligent Crash Processor for OSS-Fuzz
Seamless integration with existing infrastructure
"""

import os
import sys
import json
import asyncio
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add tools to path
sys.path.append('/opt/oss-fuzz/tools/embedding_intelligence')

try:
    from lean_crash_analyzer import LeanEmbeddingIntelligence, analyze_crash_with_intelligence
    INTELLIGENCE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Embedding intelligence not available: {e}")
    INTELLIGENCE_AVAILABLE = False

class OSSFuzzIntelligentProcessor:
    """Intelligent processor that integrates with existing OSS-Fuzz workflow."""
    
    def __init__(self, project_name: Optional[str] = None):
        self.project_name = project_name
        self.enabled = self._check_if_enabled()
        self.config = self._load_config()
        self.results_dir = Path('/tmp/oss_fuzz_intelligence')
        self.results_dir.mkdir(exist_ok=True)
        
        if self.enabled and INTELLIGENCE_AVAILABLE:
            self.intelligence = LeanEmbeddingIntelligence(self.config)
            print(f"🧠 Embedding intelligence enabled for {project_name or 'all projects'}")
        else:
            self.intelligence = None
            if self.enabled:
                print("⚠️ Embedding intelligence requested but not available")
    
    def _check_if_enabled(self) -> bool:
        """Check if embedding intelligence is enabled."""
        return (
            os.environ.get('ENABLE_EMBEDDING_INTELLIGENCE', '').lower() == 'true' or
            os.environ.get('OSS_FUZZ_INTELLIGENCE', '').lower() == 'true'
        )
    
    def _load_config(self) -> Dict:
        """Load configuration."""
        return {
            'cache_dir': os.environ.get('EMBEDDING_CACHE_DIR', '/tmp/oss_fuzz_embeddings'),
            'daily_budget': float(os.environ.get('EMBEDDING_BUDGET_DAILY', '2.0')),
            'enable_embeddings': self.enabled,
            'similarity_threshold': 0.8,
            'project_name': self.project_name,
        }
    
    def process_crash_file(self, crash_file_path: str) -> Dict:
        """Process crash file with intelligence."""
        
        # Load crash report
        crash_report = self._load_crash_file(crash_file_path)
        
        if not crash_report:
            return {'error': 'Could not load crash file', 'file': crash_file_path}
        
        # Add context
        crash_report = self._add_crash_context(crash_report, crash_file_path)
        
        # Process with intelligence if available
        if self.intelligence:
            try:
                result = self.intelligence.analyze_crash_intelligently(crash_report)
                
                # Save results
                self._save_results(result, crash_file_path)
                
                # Print summary
                self._print_intelligence_summary(result)
                
                return result
                
            except Exception as e:
                print(f"Intelligence processing failed: {e}")
                return self._fallback_processing(crash_report, crash_file_path)
        else:
            return self._fallback_processing(crash_report, crash_file_path)
    
    def _load_crash_file(self, crash_file_path: str) -> Optional[Dict]:
        """Load crash file in various formats."""
        crash_path = Path(crash_file_path)
        
        if not crash_path.exists():
            print(f"Crash file not found: {crash_file_path}")
            return None
        
        try:
            content = crash_path.read_text(encoding='utf-8', errors='ignore')
            
            # Try JSON format first
            if crash_path.suffix == '.json':
                return json.loads(content)
            
            # Parse text-based crash report
            return self._parse_text_crash_report(content, crash_file_path)
            
        except Exception as e:
            print(f"Error loading crash file {crash_file_path}: {e}")
            return None
    
    def _parse_text_crash_report(self, content: str, file_path: str) -> Dict:
        """Parse text-based crash report (AddressSanitizer, etc.)."""
        
        crash_report = {
            'crash_type': 'unknown',
            'error_message': '',
            'stack_trace': '',
            'input_info': {},
            'sanitizer_output': content,
            'source_file': file_path
        }
        
        # Extract crash type
        content_lower = content.lower()
        if 'heap-buffer-overflow' in content_lower:
            crash_report['crash_type'] = 'heap_buffer_overflow'
        elif 'stack-buffer-overflow' in content_lower:
            crash_report['crash_type'] = 'stack_buffer_overflow'
        elif 'use-after-free' in content_lower:
            crash_report['crash_type'] = 'use_after_free'
        elif 'double-free' in content_lower:
            crash_report['crash_type'] = 'double_free'
        elif 'segv' in content_lower or 'segmentation' in content_lower:
            crash_report['crash_type'] = 'segmentation_fault'
        elif 'abort' in content_lower:
            crash_report['crash_type'] = 'abort'
        
        # Extract error message (first line with error info)
        lines = content.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['error', 'overflow', 'sanitizer']):
                crash_report['error_message'] = line.strip()
                break
        
        # Extract stack trace
        stack_start = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('#0') or 'at ' in line:
                stack_start = i
                break
        
        if stack_start >= 0:
            # Find end of stack trace
            stack_end = stack_start + 1
            while stack_end < len(lines) and (
                lines[stack_end].strip().startswith('#') or 
                'at ' in lines[stack_end] or
                lines[stack_end].strip() == ''
            ):
                stack_end += 1
            
            crash_report['stack_trace'] = '\n'.join(lines[stack_start:stack_end])
        
        return crash_report
    
    def _add_crash_context(self, crash_report: Dict, file_path: str) -> Dict:
        """Add additional context to crash report."""
        
        # Add file information
        file_path_obj = Path(file_path)
        crash_report['crash_context'] = {
            'file_name': file_path_obj.name,
            'file_path': str(file_path_obj),
            'file_size': file_path_obj.stat().st_size if file_path_obj.exists() else 0,
            'project_name': self.project_name
        }
        
        # Try to find corresponding input file
        input_file = self._find_input_file(file_path)
        if input_file:
            crash_report['input_info'] = self._analyze_input_file(input_file)
        
        return crash_report
    
    def _find_input_file(self, crash_file_path: str) -> Optional[str]:
        """Find the input file that caused this crash."""
        crash_path = Path(crash_file_path)
        
        # Look for common input file patterns
        possible_inputs = [
            crash_path.with_suffix('.input'),
            crash_path.parent / 'testcase',
            crash_path.parent / 'crash-input',
            crash_path.parent / f"{crash_path.stem}-input"
        ]
        
        for input_path in possible_inputs:
            if input_path.exists():
                return str(input_path)
        
        return None
    
    def _analyze_input_file(self, input_file_path: str) -> Dict:
        """Analyze input file characteristics."""
        input_path = Path(input_file_path)
        
        if not input_path.exists():
            return {}
        
        try:
            file_size = input_path.stat().st_size
            
            # Read file content for analysis
            with open(input_path, 'rb') as f:
                content = f.read()
            
            return {
                'input_file_path': str(input_path),
                'size': file_size,
                'type': self._determine_input_type(content),
                'entropy': self._calculate_entropy(content) if content else 0.0
            }
            
        except Exception as e:
            print(f"Error analyzing input file {input_file_path}: {e}")
            return {'size': 0, 'type': 'unknown'}
    
    def _determine_input_type(self, content: bytes) -> str:
        """Determine input file type."""
        if not content:
            return 'empty'
        
        # Check magic bytes
        if content.startswith(b'\x7fELF'):
            return 'elf'
        elif content.startswith(b'MZ'):
            return 'pe'
        elif content.startswith(b'\x89PNG'):
            return 'png'
        elif content.startswith(b'\xff\xd8\xff'):
            return 'jpeg'
        elif content.startswith(b'%PDF'):
            return 'pdf'
        elif all(32 <= b <= 126 or b in [9, 10, 13] for b in content[:100]):
            return 'text'
        else:
            return 'binary'
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy."""
        if not data:
            return 0.0
        
        # Count byte frequencies
        byte_counts = [0] * 256
        for byte in data:
            byte_counts[byte] += 1
        
        # Calculate entropy
        entropy = 0.0
        data_len = len(data)
        
        for count in byte_counts:
            if count > 0:
                probability = count / data_len
                entropy -= probability * (probability.bit_length() - 1)
        
        return entropy
    
    def _save_results(self, result: Dict, crash_file_path: str):
        """Save analysis results."""
        crash_name = Path(crash_file_path).stem
        result_file = self.results_dir / f"{crash_name}_intelligence.json"
        
        # Make result JSON serializable
        serializable_result = self._make_json_serializable(result)
        
        with open(result_file, 'w') as f:
            json.dump(serializable_result, f, indent=2)
        
        print(f"📊 Results saved to: {result_file}")
    
    def _make_json_serializable(self, obj: Any) -> Any:
        """Make object JSON serializable."""
        if hasattr(obj, 'tolist'):  # numpy array
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return self._make_json_serializable(obj.__dict__)
        else:
            return obj
    
    def _print_intelligence_summary(self, result: Dict):
        """Print intelligence summary."""
        print("\n🧠 EMBEDDING INTELLIGENCE SUMMARY")
        print("=" * 50)
        
        # Basic info
        priority = result.get('priority_score', 0)
        exploit_risk = result.get('exploit_risk_score', 0)
        
        print(f"Priority Score: {priority:.2f}/1.0")
        print(f"Exploit Risk: {exploit_risk:.2f}/1.0")
        
        # Vulnerability info
        vuln_category = result.get('vulnerability_category', 'unknown')
        print(f"Vulnerability Type: {vuln_category}")
        
        # Clustering info
        cluster_info = result.get('cluster_analysis', {})
        if cluster_info.get('is_duplicate'):
            print(f"⚠️ Duplicate crash (cluster size: {cluster_info.get('cluster_size', 1)})")
        elif cluster_info.get('is_novel'):
            print("🆕 Novel crash pattern detected")
        
        # Recommendations
        recommendations = result.get('recommended_actions', [])
        if recommendations:
            print(f"\n💡 Recommendations ({len(recommendations)}):")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"  {i}. {rec.get('title', 'Unknown')}")
        
        # Test cases
        test_cases = result.get('test_cases', [])
        if test_cases:
            print(f"\n🧪 Generated test cases: {len(test_cases)}")
        
        # Cost info
        stats = result.get('intelligence_stats', {})
        if stats:
            processing_time = stats.get('processing_time_seconds', 0)
            cost = stats.get('estimated_cost', 0)
            print(f"\n⏱️ Processing: {processing_time:.2f}s | Cost: ${cost:.4f}")
        
        print("=" * 50)
    
    def _fallback_processing(self, crash_report: Dict, file_path: str) -> Dict:
        """Fallback processing without intelligence."""
        return {
            'crash_signature': f"basic_{hash(str(crash_report)) % 10000}",
            'crash_type': crash_report.get('crash_type', 'unknown'),
            'fallback_mode': True,
            'file_path': file_path,
            'basic_info': {
                'has_stack_trace': bool(crash_report.get('stack_trace')),
                'has_error_message': bool(crash_report.get('error_message')),
                'sanitizer_output_length': len(crash_report.get('sanitizer_output', ''))
            }
        }

def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print("Usage: python intelligent_crash_processor.py <crash_file> [project_name]")
        print("")
        print("Environment variables:")
        print("  ENABLE_EMBEDDING_INTELLIGENCE=true  # Enable intelligence")
        print("  GOOGLE_API_KEY=your_key             # Gemini API key") 
        print("  EMBEDDING_BUDGET_DAILY=2.0          # Daily budget ($)")
        sys.exit(1)
    
    crash_file = sys.argv[1]
    project_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    processor = OSSFuzzIntelligentProcessor(project_name)
    result = processor.process_crash_file(crash_file)
    
    # Print final result
    if result.get('error'):
        print(f"❌ Error: {result['error']}")
        sys.exit(1)
    else:
        print(f"✅ Crash analysis completed")
        if processor.intelligence:
            stats = processor.intelligence.get_statistics()
            print(f"📈 Session stats: {stats['performance']['crashes_analyzed']} crashes analyzed")

if __name__ == "__main__":
    main()