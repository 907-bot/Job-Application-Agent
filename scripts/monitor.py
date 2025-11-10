#!/usr/bin/env python3
"""
Monitor Script
Monitors application health and performance
Usage: python scripts/monitor.py [options]
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import psutil
import requests


class ApplicationMonitor:
    """Monitor application health and metrics"""
    
    def __init__(self, app_url: str = "http://localhost:7860", interval: int = 60):
        """Initialize monitor"""
        self.app_url = app_url
        self.interval = interval
        self.logger = self._setup_logging()
        self.metrics = []
        
        self.logger.info(f"Monitor initialized - URL: {app_url}, Interval: {interval}s")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger('monitor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def check_api_health(self) -> Dict:
        """Check API health"""
        try:
            response = requests.get(f"{self.app_url}/status", timeout=5)
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'response_time': response.elapsed.total_seconds(),
                    'status_code': 200
                }
            else:
                return {
                    'status': 'unhealthy',
                    'response_time': response.elapsed.total_seconds(),
                    'status_code': response.status_code
                }
        except requests.exceptions.ConnectionError:
            return {'status': 'unreachable', 'error': 'Connection refused'}
        except requests.exceptions.Timeout:
            return {'status': 'timeout', 'error': 'Request timeout'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def get_system_metrics(self) -> Dict:
        """Get system resource metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_available_gb': psutil.virtual_memory().available / (1024**3),
            'disk_percent': psutil.disk_usage('/').percent,
            'process_count': len(psutil.pids()),
        }
    
    def get_application_metrics(self) -> Dict:
        """Get application-specific metrics"""
        metrics = {}
        
        # Check log file size
        log_file = Path('logs/app.log')
        if log_file.exists():
            metrics['log_file_size_mb'] = log_file.stat().st_size / (1024**2)
        
        # Check model file
        model_files = list(Path('models/').glob('*.pt'))
        if model_files:
            metrics['model_count'] = len(model_files)
            metrics['latest_model'] = max(model_files, key=lambda p: p.stat().st_mtime).name
        
        # Check cache
        cache_dir = Path('cache/')
        if cache_dir.exists():
            cache_files = list(cache_dir.glob('*'))
            metrics['cache_files'] = len(cache_files)
        
        return metrics
    
    def collect_metrics(self) -> Dict:
        """Collect all metrics"""
        timestamp = datetime.now().isoformat()
        
        metrics = {
            'timestamp': timestamp,
            'api_health': self.check_api_health(),
            'system': self.get_system_metrics(),
            'application': self.get_application_metrics()
        }
        
        self.metrics.append(metrics)
        
        # Keep only last 1000 metrics in memory
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]
        
        return metrics
    
    def log_metrics(self, metrics: Dict):
        """Log metrics"""
        api_status = metrics['api_health']['status']
        cpu = metrics['system']['cpu_percent']
        memory = metrics['system']['memory_percent']
        
        status_emoji = '✅' if api_status == 'healthy' else '⚠️' if api_status in ['timeout', 'unhealthy'] else '❌'
        
        self.logger.info(
            f"{status_emoji} API: {api_status} | "
            f"CPU: {cpu:.1f}% | "
            f"Memory: {memory:.1f}% | "
            f"Disk: {metrics['system']['disk_percent']:.1f}%"
        )
    
    def check_thresholds(self, metrics: Dict) -> List[str]:
        """Check if metrics exceed thresholds"""
        alerts = []
        
        # CPU threshold
        if metrics['system']['cpu_percent'] > 80:
            alerts.append(f"⚠️ High CPU usage: {metrics['system']['cpu_percent']:.1f}%")
        
        # Memory threshold
        if metrics['system']['memory_percent'] > 85:
            alerts.append(f"⚠️ High memory usage: {metrics['system']['memory_percent']:.1f}%")
        
        # Disk threshold
        if metrics['system']['disk_percent'] > 90:
            alerts.append(f"⚠️ High disk usage: {metrics['system']['disk_percent']:.1f}%")
        
        # API health
        if metrics['api_health']['status'] == 'unreachable':
            alerts.append("❌ Application API is unreachable")
        
        # Log file size
        log_size = metrics['application'].get('log_file_size_mb', 0)
        if log_size > 500:
            alerts.append(f"⚠️ Large log file: {log_size:.1f} MB")
        
        return alerts
    
    def save_metrics(self, filepath: str):
        """Save metrics to file"""
        with open(filepath, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        self.logger.info(f"Metrics saved to {filepath}")
    
    def get_summary(self) -> Dict:
        """Get metrics summary"""
        if not self.metrics:
            return {}
        
        cpu_values = [m['system']['cpu_percent'] for m in self.metrics]
        memory_values = [m['system']['memory_percent'] for m in self.metrics]
        
        return {
            'total_samples': len(self.metrics),
            'cpu_avg': sum(cpu_values) / len(cpu_values),
            'cpu_max': max(cpu_values),
            'memory_avg': sum(memory_values) / len(memory_values),
            'memory_max': max(memory_values),
        }
    
    def run_continuous(self, duration: int = None):
        """Run monitoring continuously"""
        self.logger.info(f"Starting continuous monitoring (interval: {self.interval}s)")
        
        start_time = time.time()
        sample_count = 0
        
        try:
            while True:
                if duration and (time.time() - start_time) > duration:
                    break
                
                metrics = self.collect_metrics()
                self.log_metrics(metrics)
                
                alerts = self.check_thresholds(metrics)
                for alert in alerts:
                    self.logger.warning(alert)
                
                sample_count += 1
                
                time.sleep(self.interval)
        
        except KeyboardInterrupt:
            self.logger.info("\nMonitoring stopped by user")
        
        finally:
            # Print summary
            summary = self.get_summary()
            self.logger.info("\nMonitoring Summary:")
            self.logger.info(f"  Samples: {summary.get('total_samples', 0)}")
            self.logger.info(f"  CPU Avg: {summary.get('cpu_avg', 0):.1f}%")
            self.logger.info(f"  CPU Max: {summary.get('cpu_max', 0):.1f}%")
            self.logger.info(f"  Memory Avg: {summary.get('memory_avg', 0):.1f}%")
            self.logger.info(f"  Memory Max: {summary.get('memory_max', 0):.1f}%")
            
            # Save metrics
            metrics_file = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.save_metrics(metrics_file)
    
    def run_once(self):
        """Run monitoring once"""
        self.logger.info("Collecting metrics...")
        
        metrics = self.collect_metrics()
        self.log_metrics(metrics)
        
        alerts = self.check_thresholds(metrics)
        if alerts:
            self.logger.warning("Alerts:")
            for alert in alerts:
                self.logger.warning(f"  {alert}")
        
        return metrics


def main():
    """Main monitoring function"""
    parser = argparse.ArgumentParser(description='Monitor application health')
    parser.add_argument(
        '--url',
        default='http://localhost:7860',
        help='Application URL (default: http://localhost:7860)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Monitoring interval in seconds (default: 60)'
    )
    parser.add_argument(
        '--duration',
        type=int,
        help='Monitoring duration in seconds (default: infinite)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run monitoring once and exit'
    )
    parser.add_argument(
        '--save',
        action='store_true',
        help='Save metrics to file'
    )
    
    args = parser.parse_args()
    
    # Initialize monitor
    monitor = ApplicationMonitor(app_url=args.url, interval=args.interval)
    
    # Run monitoring
    if args.once:
        metrics = monitor.run_once()
        if args.save:
            monitor.save_metrics(f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        return 0
    else:
        monitor.run_continuous(duration=args.duration)
        if args.save:
            monitor.save_metrics(f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        return 0


if __name__ == '__main__':
    sys.exit(main())
