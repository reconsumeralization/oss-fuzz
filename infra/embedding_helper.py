#!/usr/bin/env python3
"""
Embedding Intelligence Helper for OSS-Fuzz
Minimal integration with existing helper.py
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, List

def is_intelligence_enabled() -> bool:
    """Check if embedding intelligence is enabled."""
    return (
        os.environ.get('ENABLE_EMBEDDING_INTELLIGENCE', '').lower() == 'true' or
        os.environ.get('OSS_FUZZ_INTELLIGENCE', '').lower() == 'true'
    )

def analyze_crash_intelligently(crash_file_path: str, project_name: Optional[str] = None) -> Dict:
    """Analyze crash with embedding intelligence."""
    
    if not is_intelligence_enabled():
        return {'intelligence_used': False, 'reason': 'not_enabled'}
    
    try:
        # Use the intelligent crash processor
        cmd = [
            sys.executable, 
            '/opt/oss-fuzz/infra/intelligent_crash_processor.py',
            crash_file_path
        ]
        
        if project_name:
            cmd.append(project_name)
        
        # Set environment for subprocess
        env = os.environ.copy()
        env['PYTHONPATH'] = '/opt/oss-fuzz:/opt/oss-fuzz/tools/embedding_intelligence'
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout
            env=env
        )
        
        if result.returncode == 0:
            return {
                'intelligence_used': True,
                'success': True,
                'stdout': result.stdout,
                'processing_time': time.time()  # Would track actual time
            }
        else:
            return {
                'intelligence_used': True,
                'success': False,
                'error': result.stderr,
                'stdout': result.stdout
            }
            
    except subprocess.TimeoutExpired:
        return {
            'intelligence_used': True,
            'success': False,
            'error': 'Intelligence processing timed out'
        }
    except Exception as e:
        return {
            'intelligence_used': True,
            'success': False,
            'error': str(e)
        }

def enhance_build_with_intelligence(project_name: str, build_dir: str) -> Dict:
    """Enhance build process with intelligence."""
    
    if not is_intelligence_enabled():
        return {'enhanced': False}
    
    # Pre-build analysis
    enhancement_info = {
        'enhanced': True,
        'project_name': project_name,
        'build_dir': build_dir,
        'intelligence_cache_dir': f'/tmp/oss_fuzz_embeddings/{project_name}',
        'recommendations': []
    }
    
    # Create project-specific cache directory
    cache_dir = Path(enhancement_info['intelligence_cache_dir'])
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Add environment variables for the build
    os.environ['PROJECT_INTELLIGENCE_CACHE'] = str(cache_dir)
    os.environ['OSS_FUZZ_PROJECT'] = project_name
    
    print(f"🧠 Intelligence enhancement enabled for {project_name}")
    
    return enhancement_info

def process_fuzzing_results_intelligently(results_dir: str, project_name: str) -> Dict:
    """Process fuzzing results with intelligence."""
    
    if not is_intelligence_enabled():
        return {'processed': False}
    
    results_path = Path(results_dir)
    intelligence_results = {
        'processed': True,
        'project_name': project_name,
        'crash_analyses': [],
        'summary': {
            'total_crashes': 0,
            'novel_crashes': 0,
            'critical_crashes': 0,
            'intelligence_cost': 0.0
        }
    }
    
    # Find all crash files
    crash_files = list(results_path.glob('**/*crash*')) + list(results_path.glob('**/*asan*'))
    
    for crash_file in crash_files:
        if crash_file.is_file() and crash_file.stat().st_size > 0:
            try:
                analysis_result = analyze_crash_intelligently(str(crash_file), project_name)
                
                if analysis_result.get('success'):
                    intelligence_results['crash_analyses'].append({
                        'crash_file': str(crash_file),
                        'analysis': analysis_result
                    })
                    
                    intelligence_results['summary']['total_crashes'] += 1
                    
                    # Update summary based on analysis
                    # (would parse the actual results)
                    
            except Exception as e:
                print(f"Error analyzing {crash_file}: {e}")
                continue
    
    return intelligence_results

def get_intelligence_statistics() -> Dict:
    """Get intelligence usage statistics."""
    
    stats = {
        'enabled': is_intelligence_enabled(),
        'cache_size': 0,
        'daily_cost': 0.0,
        'crashes_analyzed_today': 0
    }
    
    if not stats['enabled']:
        return stats
    
    # Load statistics from cache
    cache_dir = Path('/tmp/oss_fuzz_embeddings')
    if cache_dir.exists():
        try:
            # Count cached embeddings
            cache_files = list(cache_dir.glob('**/*.pkl'))
            stats['cache_size'] = len(cache_files)
            
            # Load daily cost if available
            import json
            cost_file = cache_dir / 'daily_cost.json'
            if cost_file.exists():
                with open(cost_file) as f:
                    cost_data = json.load(f)
                    today = time.strftime('%Y-%m-%d')
                    stats['daily_cost'] = cost_data.get(today, 0.0)
                    
        except Exception as e:
            print(f"Error loading intelligence statistics: {e}")
    
    return stats

def print_intelligence_banner():
    """Print intelligence banner if enabled."""
    
    if is_intelligence_enabled():
        print("🧠" + "="*60)
        print("   OSS-FUZZ EMBEDDING INTELLIGENCE ENABLED")
        
        stats = get_intelligence_statistics()
        budget = float(os.environ.get('EMBEDDING_BUDGET_DAILY', '2.0'))
        
        print(f"   Daily Budget: ${budget:.2f} | Used: ${stats['daily_cost']:.4f}")
        print(f"   Cache Size: {stats['cache_size']} embeddings")
        print("   Environment: ENABLE_EMBEDDING_INTELLIGENCE=true")
        print("="*68)
        print()

def setup_intelligence_environment(project_name: str):
    """Setup environment for embedding intelligence."""
    
    if not is_intelligence_enabled():
        return
    
    # Create project-specific directories
    base_dir = Path('/tmp/oss_fuzz_embeddings')
    project_dir = base_dir / project_name
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Set environment variables
    os.environ['OSS_FUZZ_PROJECT'] = project_name
    os.environ['PROJECT_INTELLIGENCE_CACHE'] = str(project_dir)
    
    # Verify API key
    if not os.environ.get('GOOGLE_API_KEY'):
        print("⚠️ Warning: GOOGLE_API_KEY not set. Embedding features will be limited.")
    
    print(f"🧠 Intelligence environment ready for {project_name}")

# Integration points for existing helper.py functions
def wrap_build_fuzzers_with_intelligence(original_build_func):
    """Wrapper for build_fuzzers function."""
    
    def enhanced_build_fuzzers(*args, **kwargs):
        project_name = kwargs.get('project_name') or (args[0] if args else 'unknown')
        
        # Setup intelligence
        if is_intelligence_enabled():
            setup_intelligence_environment(project_name)
            print_intelligence_banner()
        
        # Call original function
        result = original_build_func(*args, **kwargs)
        
        # Post-build intelligence processing
        if is_intelligence_enabled() and result:
            enhance_build_with_intelligence(project_name, kwargs.get('build_dir', '/out'))
        
        return result
    
    return enhanced_build_fuzzers

def wrap_reproduce_with_intelligence(original_reproduce_func):
    """Wrapper for reproduce function."""
    
    def enhanced_reproduce(*args, **kwargs):
        # Call original function
        result = original_reproduce_func(*args, **kwargs)
        
        # Analyze crash intelligently if reproduce found a crash
        if is_intelligence_enabled() and result:
            project_name = kwargs.get('project_name') or (args[0] if args else 'unknown')
            
            # Look for crash files in common locations
            common_crash_paths = [
                '/tmp/crash-*',
                '/tmp/*crash*',
                '/out/*crash*'
            ]
            
            import glob
            for pattern in common_crash_paths:
                crash_files = glob.glob(pattern)
                for crash_file in crash_files:
                    try:
                        analysis = analyze_crash_intelligently(crash_file, project_name)
                        if analysis.get('success'):
                            print(f"🧠 Intelligent analysis completed for {crash_file}")
                    except Exception as e:
                        print(f"Intelligence analysis error: {e}")
        
        return result
    
    return enhanced_reproduce

# Easy integration check
def check_integration():
    """Check if integration is working."""
    
    print("🔍 Checking OSS-Fuzz Embedding Intelligence Integration...")
    
    checks = {
        'intelligence_enabled': is_intelligence_enabled(),
        'api_key_set': bool(os.environ.get('GOOGLE_API_KEY')),
        'cache_directory': Path('/tmp/oss_fuzz_embeddings').exists(),
        'processor_available': Path('/opt/oss-fuzz/infra/intelligent_crash_processor.py').exists(),
        'analyzer_available': Path('/opt/oss-fuzz/tools/embedding_intelligence/lean_crash_analyzer.py').exists()
    }
    
    print("\nIntegration Status:")
    for check, status in checks.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {check}: {status}")
    
    if all(checks.values()):
        print("\n🎉 Integration is fully ready!")
        stats = get_intelligence_statistics()
        print(f"   Cache size: {stats['cache_size']} embeddings")
        print(f"   Daily cost: ${stats['daily_cost']:.4f}")
    else:
        print("\n⚠️ Integration issues detected. See above for details.")
        
        # Provide setup instructions
        if not checks['intelligence_enabled']:
            print("\n   To enable: export ENABLE_EMBEDDING_INTELLIGENCE=true")
        if not checks['api_key_set']:
            print("   To set API key: export GOOGLE_API_KEY=your_key_here")
    
    return all(checks.values())

if __name__ == "__main__":
    check_integration()