#!/usr/bin/env python3
"""
Lean, Cost-Optimized Crash Intelligence for OSS-Fuzz
Direct integration with existing crash_analysis.py
Maximum ROI, minimal API costs
"""

import os
import sys
import json
import hashlib
import pickle
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
import numpy as np
from collections import defaultdict, Counter

# Import existing crash analyzer
try:
    from .crash_analysis import IntelligentCrashAnalyzer
    CRASH_ANALYSIS_AVAILABLE = True
except ImportError:
    print("Warning: crash_analysis.py not found, using standalone mode")
    CRASH_ANALYSIS_AVAILABLE = False

# GTM emitter (optional)
try:
    from .gtm_emitter import emit_embedding_event  # type: ignore
    GTM_EMITTER_AVAILABLE = True
except Exception:
    try:
        from gtm_emitter import emit_embedding_event  # type: ignore
        GTM_EMITTER_AVAILABLE = True
    except Exception:
        GTM_EMITTER_AVAILABLE = False

class LeanEmbeddingIntelligence:
    """Lean embedding intelligence that extends existing crash analysis."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._get_default_config()
        
        # Cost tracking
        self.daily_budget = float(os.environ.get('EMBEDDING_BUDGET_DAILY', '2.00'))
        self.cost_per_embedding = 0.0001  # $0.0001 per embedding
        self.current_daily_cost = self._load_daily_cost()
        
        # Performance tracking
        self.stats = {
            'crashes_analyzed': 0,
            'embeddings_generated': 0,
            'cache_hits': 0,
            'api_calls_saved': 0,
            'processing_time': 0.0
        }
        
        # Caching system
        self.cache_dir = Path(self.config.get('cache_dir', '/tmp/oss_fuzz_embeddings'))
        self.cache_dir.mkdir(exist_ok=True)
        self.embedding_cache = self._load_embedding_cache()
        
        # Existing analyzer integration
        if CRASH_ANALYSIS_AVAILABLE:
            self.base_analyzer = IntelligentCrashAnalyzer(self.config)
        else:
            self.base_analyzer = None
            
        # High-impact features only
        self.vulnerability_patterns = self._load_vulnerability_patterns()
        self.crash_clusters = defaultdict(list)
    
    def _get_default_config(self) -> Dict:
        """Get optimized default configuration."""
        return {
            'cache_dir': '/tmp/oss_fuzz_embeddings',
            'similarity_threshold': 0.8,
            'high_value_threshold': 0.7,
            'max_cache_size': 10000,
            'enable_embeddings': os.environ.get('ENABLE_EMBEDDING_INTELLIGENCE', '').lower() == 'true'
        }
    
    def analyze_crash_intelligently(self, crash_report: Dict) -> Dict:
        """Main entry point: analyze crash with embedding intelligence."""
        start_time = time.time()
        
        try:
            # PHASE 1: Fast local analysis (FREE)
            enhanced_analysis = self._fast_local_enhancement(crash_report)
            
            # PHASE 2: Selective embedding analysis (COSTS MONEY)
            if self._should_use_embeddings(enhanced_analysis):
                embedding_enhancement = self._selective_embedding_analysis(crash_report)
                enhanced_analysis.update(embedding_enhancement)
            
            # PHASE 3: Generate actionable outputs
            enhanced_analysis['recommended_actions'] = self._generate_recommendations(enhanced_analysis)
            enhanced_analysis['test_cases'] = self._generate_smart_test_cases(crash_report, enhanced_analysis)
            
            # Update statistics
            processing_time = time.time() - start_time
            self.stats['crashes_analyzed'] += 1
            self.stats['processing_time'] += processing_time
            
            enhanced_analysis['intelligence_stats'] = {
                'processing_time_seconds': processing_time,
                'embedding_used': enhanced_analysis.get('embedding_analysis_used', False),
                'estimated_cost': enhanced_analysis.get('estimated_cost', 0.0),
                'cache_hit': enhanced_analysis.get('cache_hit', False)
            }
            
            # Emit GTM protobuf telemetry (best-effort/no-op if unavailable)
            if GTM_EMITTER_AVAILABLE:
                try:
                    emit_embedding_event(
                        project_name=self.config.get('project_name'),
                        crash_report=crash_report,
                        analysis=enhanced_analysis,
                        config=self.config,
                        model_name='models/embedding-001' if enhanced_analysis.get('embedding_analysis_used') else ''
                    )
                except Exception:
                    pass
            
            return enhanced_analysis
            
        except Exception as e:
            print(f"Error in crash intelligence: {e}")
            # Fallback to basic analysis
            return self._fallback_analysis(crash_report)
    
    def _fast_local_enhancement(self, crash_report: Dict) -> Dict:
        """Fast, free enhancements using local analysis."""
        
        # Start with existing analysis if available
        if self.base_analyzer:
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                base_result = loop.run_until_complete(self.base_analyzer.analyze_crash(crash_report))
                loop.close()
                enhanced = base_result.copy()
            except Exception as e:
                print(f"Base analyzer error: {e}")
                enhanced = {}
        else:
            enhanced = {}
        
        # Add fast, high-value enhancements
        enhanced.update({
            'crash_signature': self._generate_fast_signature(crash_report),
            'exploit_risk_score': self._calculate_exploit_risk(crash_report),
            'vulnerability_category': self._categorize_vulnerability(crash_report),
            'deduplication_key': self._generate_dedup_key(crash_report),
            'priority_score': self._calculate_priority_score(crash_report)
        })
        
        # Fast clustering using heuristics
        cluster_info = self._fast_cluster_analysis(enhanced['deduplication_key'])
        enhanced['cluster_analysis'] = cluster_info
        
        # Pattern matching against known vulnerabilities
        vuln_matches = self._match_vulnerability_patterns(crash_report)
        enhanced['vulnerability_matches'] = vuln_matches
        
        return enhanced
    
    def _should_use_embeddings(self, analysis: Dict) -> bool:
        """Decide if crash warrants expensive embedding analysis."""
        
        # Check budget first
        if self.current_daily_cost >= self.daily_budget:
            return False
        
        # Check if embeddings are enabled
        if not self.config.get('enable_embeddings', False):
            return False
        
        # High-value criteria
        high_value_indicators = [
            analysis.get('priority_score', 0) > 0.8,  # High priority
            analysis.get('exploit_risk_score', 0) > 0.7,  # High exploit risk
            analysis.get('cluster_analysis', {}).get('is_novel', False),  # Novel crash
            len(analysis.get('vulnerability_matches', [])) == 0,  # No known patterns
            'critical' in analysis.get('vulnerability_category', '').lower()  # Critical category
        ]
        
        # Use embeddings if ANY high-value criterion is met
        return any(high_value_indicators)
    
    def _selective_embedding_analysis(self, crash_report: Dict) -> Dict:
        """Selective embedding analysis for high-value crashes only."""
        
        # Create optimized crash text (minimize tokens = minimize cost)
        crash_text = self._create_optimized_crash_text(crash_report)
        
        # Generate cache key
        cache_key = hashlib.sha256(crash_text.encode()).hexdigest()
        
        # Check cache first
        cached_embedding = self._get_cached_embedding(cache_key)
        
        if cached_embedding is not None:
            self.stats['cache_hits'] += 1
            embedding_result = {
                'embedding_analysis_used': True,
                'cache_hit': True,
                'estimated_cost': 0.0,
                'similar_crashes': self._find_similar_crashes_fast(cached_embedding)
            }
        else:
            # Generate new embedding (costs money)
            embedding_result = self._generate_new_embedding(crash_text, cache_key)
        
        return embedding_result
    
    def _generate_new_embedding(self, crash_text: str, cache_key: str) -> Dict:
        """Generate new embedding with cost tracking."""
        
        try:
            # Only import when actually needed
            import google.generativeai as genai
            
            # Configure API key
            api_key = os.environ.get('GOOGLE_API_KEY')
            if not api_key:
                print("Warning: GOOGLE_API_KEY not set, skipping embedding generation")
                return {'embedding_analysis_used': False, 'error': 'no_api_key'}
            
            genai.configure(api_key=api_key)
            
            # Generate embedding
            embedding_response = genai.embed_content(
                model='models/embedding-001',
                content=crash_text,
                task_type="classification"
            )
            
            embedding = np.array(embedding_response['embedding'])
            
            # Cache the result
            self._cache_embedding(cache_key, embedding)
            
            # Update cost tracking
            self.current_daily_cost += self.cost_per_embedding
            self._save_daily_cost()
            
            self.stats['embeddings_generated'] += 1
            
            # Find similar crashes
            similar_crashes = self._find_similar_crashes_fast(embedding)
            
            return {
                'embedding_analysis_used': True,
                'cache_hit': False,
                'estimated_cost': self.cost_per_embedding,
                'similar_crashes': similar_crashes,
                'embedding_confidence': self._calculate_embedding_confidence(embedding)
            }
            
        except Exception as e:
            print(f"Embedding generation failed: {e}")
            return {
                'embedding_analysis_used': False,
                'error': str(e),
                'estimated_cost': 0.0
            }
    
    def _create_optimized_crash_text(self, crash_report: Dict) -> str:
        """Create cost-optimized text for embedding (minimize tokens)."""
        
        parts = []
        
        # Essential information only
        crash_type = crash_report.get('crash_type', 'unknown')
        parts.append(f"CRASH: {crash_type}")
        
        # Top function from stack trace
        stack_trace = crash_report.get('stack_trace', '')
        if stack_trace:
            top_function = self._extract_top_function(stack_trace)
            if top_function:
                parts.append(f"FUNC: {top_function}")
        
        # Key error information (truncated)
        error_message = crash_report.get('error_message', '')
        if error_message:
            error_summary = error_message[:200]  # Limit to 200 chars
            parts.append(f"ERROR: {error_summary}")
        
        # Input characteristics
        input_info = crash_report.get('input_info', {})
        if input_info:
            size = input_info.get('size', 0)
            if size > 0:
                parts.append(f"INPUT_SIZE: {size}")
        
        # Keep total under 300 characters to minimize cost
        text = '\n'.join(parts)
        return text[:500]  # Hard limit
    
    def _generate_fast_signature(self, crash_report: Dict) -> str:
        """Generate crash signature without embeddings."""
        components = [
            crash_report.get('crash_type', 'unknown'),
            self._extract_top_function(crash_report.get('stack_trace', '')),
            str(hash(crash_report.get('error_message', '')) % 10000)
        ]
        
        signature = '|'.join(filter(None, components))
        return hashlib.md5(signature.encode()).hexdigest()[:12]
    
    def _calculate_exploit_risk(self, crash_report: Dict) -> float:
        """Calculate exploit risk using fast heuristics."""
        risk_score = 0.0
        
        crash_type = crash_report.get('crash_type', '').lower()
        error_message = crash_report.get('error_message', '').lower()
        
        # High risk indicators
        high_risk_patterns = [
            'heap-buffer-overflow', 'use-after-free', 'double-free',
            'buffer overflow', 'memory corruption', 'segmentation fault'
        ]
        
        for pattern in high_risk_patterns:
            if pattern in crash_type or pattern in error_message:
                risk_score += 0.3
                
        # Input size factor
        input_info = crash_report.get('input_info', {})
        input_size = input_info.get('size', 0)
        if input_size > 1000:
            risk_score += 0.2
        elif input_size > 100:
            risk_score += 0.1
            
        return min(risk_score, 1.0)
    
    def _categorize_vulnerability(self, crash_report: Dict) -> str:
        """Categorize vulnerability type."""
        crash_type = crash_report.get('crash_type', '').lower()
        error_message = crash_report.get('error_message', '').lower()
        
        if 'buffer' in crash_type + error_message:
            return 'buffer_overflow'
        elif 'use-after-free' in crash_type + error_message:
            return 'use_after_free'
        elif 'null' in crash_type + error_message:
            return 'null_pointer_dereference'
        elif 'segmentation' in crash_type + error_message:
            return 'memory_corruption'
        else:
            return 'other'
    
    def _calculate_priority_score(self, crash_report: Dict) -> float:
        """Calculate overall priority score."""
        exploit_risk = self._calculate_exploit_risk(crash_report)
        
        # Bonus for memory corruption
        memory_bonus = 0.2 if 'memory' in crash_report.get('crash_type', '').lower() else 0.0
        
        # Bonus for large inputs (potential for fuzzing)
        input_size = crash_report.get('input_info', {}).get('size', 0)
        size_bonus = 0.1 if input_size > 1000 else 0.0
        
        return min(exploit_risk + memory_bonus + size_bonus, 1.0)
    
    def _generate_dedup_key(self, crash_report: Dict) -> str:
        """Generate deduplication key."""
        key_parts = [
            crash_report.get('crash_type', 'unknown'),
            self._extract_top_function(crash_report.get('stack_trace', '')),
            self._normalize_error_message(crash_report.get('error_message', ''))
        ]
        
        key = '|'.join(filter(None, key_parts))
        return hashlib.md5(key.encode()).hexdigest()[:16]
    
    def _extract_top_function(self, stack_trace: str) -> Optional[str]:
        """Extract top function from stack trace."""
        if not stack_trace:
            return None
            
        import re
        lines = stack_trace.split('\n')
        
        for line in lines[:5]:  # Check first 5 lines
            # Common patterns
            patterns = [
                r'#0.*in\s+(\w+)',
                r'at\s+(\w+)',
                r'(\w+)\s*\(',
                r'in\s+(\w+)\s+at'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    return match.group(1)
        
        return None
    
    def _normalize_error_message(self, error_message: str) -> str:
        """Normalize error message for deduplication."""
        if not error_message:
            return ''
            
        import re
        # Remove addresses and line numbers
        normalized = re.sub(r'0x[0-9a-f]+', 'ADDR', error_message)
        normalized = re.sub(r':\d+', ':LINE', normalized)
        normalized = re.sub(r'\d+', 'NUM', normalized)
        
        return normalized[:100]  # Limit length
    
    def _fast_cluster_analysis(self, dedup_key: str) -> Dict:
        """Fast clustering analysis without embeddings."""
        
        # Check if we've seen this exact crash before
        if dedup_key in self.crash_clusters:
            cluster_size = len(self.crash_clusters[dedup_key])
            is_duplicate = True
            is_novel = False
        else:
            cluster_size = 1
            is_duplicate = False
            is_novel = True
            
        # Add to cluster
        self.crash_clusters[dedup_key].append(time.time())
        
        return {
            'is_duplicate': is_duplicate,
            'is_novel': is_novel,
            'cluster_size': cluster_size,
            'deduplication_key': dedup_key
        }
    
    def _match_vulnerability_patterns(self, crash_report: Dict) -> List[Dict]:
        """Match against known vulnerability patterns."""
        matches = []
        
        crash_type = crash_report.get('crash_type', '').lower()
        error_message = crash_report.get('error_message', '').lower()
        
        for pattern_name, pattern_info in self.vulnerability_patterns.items():
            keywords = pattern_info['keywords']
            
            # Simple keyword matching
            if any(keyword in crash_type + error_message for keyword in keywords):
                matches.append({
                    'pattern_name': pattern_name,
                    'severity': pattern_info['severity'],
                    'confidence': 0.8,  # High confidence for keyword match
                    'cve_examples': pattern_info.get('cve_examples', [])
                })
        
        return matches
    
    def _load_vulnerability_patterns(self) -> Dict:
        """Load known vulnerability patterns."""
        # Hardcoded patterns for speed (no file I/O)
        return {
            'heap_buffer_overflow': {
                'keywords': ['heap-buffer-overflow', 'heap overflow'],
                'severity': 'critical',
                'cve_examples': ['CVE-2021-44228', 'CVE-2020-1472']
            },
            'use_after_free': {
                'keywords': ['use-after-free', 'freed memory'],
                'severity': 'high', 
                'cve_examples': ['CVE-2021-30563', 'CVE-2020-6449']
            },
            'buffer_overflow': {
                'keywords': ['buffer overflow', 'stack-buffer-overflow'],
                'severity': 'high',
                'cve_examples': ['CVE-2021-3156', 'CVE-2020-14386']
            },
            'null_pointer_dereference': {
                'keywords': ['null pointer', 'segmentation fault'],
                'severity': 'medium',
                'cve_examples': ['CVE-2021-22555']
            }
        }
    
    def _generate_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Priority-based recommendations
        priority = analysis.get('priority_score', 0)
        if priority > 0.8:
            recommendations.append({
                'type': 'immediate_action',
                'title': 'Critical crash requires immediate investigation',
                'description': f'High priority crash (score: {priority:.2f}) with significant exploit potential',
                'actions': ['Investigate crash location', 'Implement bounds checking', 'Add regression test']
            })
        
        # Vulnerability-specific recommendations
        vuln_category = analysis.get('vulnerability_category', '')
        if vuln_category == 'buffer_overflow':
            recommendations.append({
                'type': 'mitigation',
                'title': 'Buffer overflow mitigation',
                'description': 'Implement safe string handling',
                'actions': ['Replace unsafe functions', 'Add input validation', 'Use safe alternatives']
            })
        
        # Clustering recommendations
        if analysis.get('cluster_analysis', {}).get('cluster_size', 1) > 1:
            recommendations.append({
                'type': 'systematic_fix',
                'title': 'Multiple similar crashes detected',
                'description': 'This appears to be part of a systematic issue',
                'actions': ['Review related crashes', 'Fix root cause', 'Enhance test coverage']
            })
        
        return recommendations
    
    def _generate_smart_test_cases(self, crash_report: Dict, analysis: Dict) -> List[Dict]:
        """Generate intelligent test cases."""
        test_cases = []
        
        input_info = crash_report.get('input_info', {})
        base_size = input_info.get('size', 100)
        
        # Size-based tests (proven effective)
        test_cases.extend([
            {
                'type': 'boundary_test',
                'description': 'Test boundary condition',
                'input_size': base_size - 1,
                'pattern': 'A' * (base_size - 1) if base_size > 1 else 'A'
            },
            {
                'type': 'overflow_test', 
                'description': 'Test buffer overflow',
                'input_size': base_size * 2,
                'pattern': 'B' * (base_size * 2)
            },
            {
                'type': 'null_bytes_test',
                'description': 'Test null byte handling',
                'input_size': base_size,
                'pattern': '\\x00' * base_size
            }
        ])
        
        # Vulnerability-specific tests
        vuln_category = analysis.get('vulnerability_category', '')
        if vuln_category == 'buffer_overflow':
            test_cases.append({
                'type': 'buffer_overflow_specific',
                'description': 'Target buffer overflow vulnerability',
                'input_size': base_size * 4,
                'pattern': 'AAAA' * (base_size)
            })
        
        return test_cases[:10]  # Limit to top 10
    
    def _fallback_analysis(self, crash_report: Dict) -> Dict:
        """Fallback analysis if intelligence fails."""
        return {
            'crash_signature': self._generate_fast_signature(crash_report),
            'fallback_mode': True,
            'basic_analysis': {
                'crash_type': crash_report.get('crash_type', 'unknown'),
                'has_stack_trace': bool(crash_report.get('stack_trace')),
                'has_error_message': bool(crash_report.get('error_message'))
            }
        }
    
    # Caching methods
    def _load_embedding_cache(self) -> Dict:
        """Load embedding cache from disk."""
        cache_file = self.cache_dir / 'embedding_cache.pkl'
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except:
                pass
        return {}
    
    def _get_cached_embedding(self, cache_key: str) -> Optional[np.ndarray]:
        """Get embedding from cache."""
        return self.embedding_cache.get(cache_key)
    
    def _cache_embedding(self, cache_key: str, embedding: np.ndarray):
        """Cache embedding to disk."""
        self.embedding_cache[cache_key] = embedding
        
        # Periodic cache save (not every time for performance)
        if len(self.embedding_cache) % 10 == 0:
            cache_file = self.cache_dir / 'embedding_cache.pkl'
            with open(cache_file, 'wb') as f:
                pickle.dump(self.embedding_cache, f)
    
    def _load_daily_cost(self) -> float:
        """Load today's cost from file."""
        cost_file = self.cache_dir / 'daily_cost.json'
        if cost_file.exists():
            try:
                with open(cost_file, 'r') as f:
                    data = json.load(f)
                    today = time.strftime('%Y-%m-%d')
                    return data.get(today, 0.0)
            except:
                pass
        return 0.0
    
    def _save_daily_cost(self):
        """Save today's cost to file."""
        cost_file = self.cache_dir / 'daily_cost.json'
        today = time.strftime('%Y-%m-%d')
        
        data = {}
        if cost_file.exists():
            try:
                with open(cost_file, 'r') as f:
                    data = json.load(f)
            except:
                pass
        
        data[today] = self.current_daily_cost
        
        with open(cost_file, 'w') as f:
            json.dump(data, f)
    
    def _find_similar_crashes_fast(self, embedding: np.ndarray) -> List[Dict]:
        """Find similar crashes using cached embeddings."""
        # For now, return placeholder (would implement similarity search)
        return []
    
    def _calculate_embedding_confidence(self, embedding: np.ndarray) -> float:
        """Calculate confidence in embedding quality."""
        # Simple heuristic: norm of embedding vector
        return min(np.linalg.norm(embedding) / 100.0, 1.0)
    
    def get_statistics(self) -> Dict:
        """Get performance and cost statistics."""
        return {
            'performance': self.stats,
            'cost_info': {
                'daily_budget': self.daily_budget,
                'current_cost': self.current_daily_cost,
                'remaining_budget': self.daily_budget - self.current_daily_cost
            },
            'cache_info': {
                'cache_size': len(self.embedding_cache),
                'cache_hit_rate': self.stats['cache_hits'] / max(self.stats['crashes_analyzed'], 1)
            }
        }

# Easy integration function
def analyze_crash_with_intelligence(crash_report: Dict, config: Optional[Dict] = None) -> Dict:
    """Main entry point for crash intelligence."""
    analyzer = LeanEmbeddingIntelligence(config)
    return analyzer.analyze_crash_intelligently(crash_report)

if __name__ == "__main__":
    # Demo mode
    sample_crash = {
        'crash_type': 'heap-buffer-overflow',
        'error_message': 'AddressSanitizer: heap-buffer-overflow on address 0x60200000eff0',
        'stack_trace': '#0 0x4f5e35 in main /src/test.c:42:5',
        'input_info': {'size': 1000, 'type': 'binary'}
    }
    
    result = analyze_crash_with_intelligence(sample_crash)
    print(json.dumps(result, indent=2, default=str))