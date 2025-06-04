"""
Metrics tracking utility for DreamOS performance monitoring.
Tracks agent execution time, memory usage, tool hit frequency, and LLM latency.
"""
import time
import psutil
import threading
import json
import os
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque

# Initialize logger
logger = logging.getLogger("metrics")

class MetricsTracker:
    """Singleton class to track various performance metrics across DreamOS"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Data structures to store metrics
        self.agent_execution_times = defaultdict(list)  # {agent_name: [execution_times]}
        self.llm_latencies = []  # List of LLM API call latencies
        self.tool_usage = defaultdict(int)  # {tool_name: count}
        self.memory_snapshots = deque(maxlen=100)  # Limited size queue of memory usage snapshots
        
        # Initialize memory tracking
        self._start_memory_tracking()
        
        # Path for metrics persistence
        self.metrics_dir = os.path.join("dreamos", "memory", "metrics")
        os.makedirs(self.metrics_dir, exist_ok=True)
        
        # Set the initialization flag
        self._initialized = True
        logger.info("Metrics tracker initialized")
    
    def _start_memory_tracking(self, interval=60):
        """Start periodic memory usage tracking"""
        def track_memory():
            while True:
                try:
                    process = psutil.Process(os.getpid())
                    memory_info = process.memory_info()
                    timestamp = time.time()
                    
                    # Store memory info
                    self.memory_snapshots.append({
                        'timestamp': timestamp,
                        'rss': memory_info.rss,  # Resident Set Size
                        'vms': memory_info.vms,  # Virtual Memory Size
                        'percent': process.memory_percent()
                    })
                    
                except Exception as e:
                    logger.error(f"Error tracking memory usage: {str(e)}")
                
                # Sleep for the interval
                time.sleep(interval)
        
        # Start memory tracking in a background thread
        thread = threading.Thread(target=track_memory, daemon=True)
        thread.start()
        logger.info(f"Started memory tracking at {interval}s intervals")
    
    def record_agent_execution(self, agent_name, execution_time):
        """Record execution time for an agent"""
        self.agent_execution_times[agent_name].append({
            'timestamp': time.time(),
            'duration': execution_time
        })
        
        # Trim list if it gets too long
        if len(self.agent_execution_times[agent_name]) > 1000:
            self.agent_execution_times[agent_name] = self.agent_execution_times[agent_name][-1000:]
    
    def record_llm_latency(self, model_name, latency, tokens_in=None, tokens_out=None):
        """Record latency for an LLM API call"""
        self.llm_latencies.append({
            'timestamp': time.time(),
            'model': model_name,
            'latency': latency,
            'tokens_in': tokens_in,
            'tokens_out': tokens_out
        })
        
        # Trim list if it gets too long
        if len(self.llm_latencies) > 1000:
            self.llm_latencies = self.llm_latencies[-1000:]
    
    def record_tool_usage(self, tool_name):
        """Record usage of a tool"""
        self.tool_usage[tool_name] += 1
    
    def get_memory_usage(self, time_range_minutes=60):
        """Get memory usage data for the specified time range"""
        now = time.time()
        cutoff = now - (time_range_minutes * 60)
        
        # Filter snapshots by time range
        filtered_snapshots = [
            snapshot for snapshot in self.memory_snapshots
            if snapshot['timestamp'] >= cutoff
        ]
        
        # Format for chart display
        timestamps = [datetime.fromtimestamp(s['timestamp']).strftime('%H:%M:%S') 
                     for s in filtered_snapshots]
        
        # Convert bytes to MB for readability
        rss_values = [s['rss'] / (1024 * 1024) for s in filtered_snapshots]
        
        return {
            'timestamps': timestamps,
            'rss_values': rss_values,
            'current_usage': rss_values[-1] if rss_values else 0
        }
    
    def get_agent_performance(self, time_range_minutes=60):
        """Get agent performance metrics for the specified time range"""
        now = time.time()
        cutoff = now - (time_range_minutes * 60)
        
        agent_stats = {}
        for agent_name, executions in self.agent_execution_times.items():
            # Filter by time range
            recent_executions = [
                ex for ex in executions
                if ex['timestamp'] >= cutoff
            ]
            
            if recent_executions:
                # Calculate average, min, max execution times
                durations = [ex['duration'] for ex in recent_executions]
                agent_stats[agent_name] = {
                    'count': len(recent_executions),
                    'avg_time': sum(durations) / len(durations),
                    'min_time': min(durations),
                    'max_time': max(durations)
                }
        
        return agent_stats
    
    def get_llm_performance(self, time_range_minutes=60):
        """Get LLM performance metrics for the specified time range"""
        now = time.time()
        cutoff = now - (time_range_minutes * 60)
        
        # Filter by time range
        recent_calls = [
            call for call in self.llm_latencies
            if call['timestamp'] >= cutoff
        ]
        
        if not recent_calls:
            return {
                'count': 0,
                'avg_latency': 0,
                'models': {}
            }
        
        # Calculate overall average latency
        latencies = [call['latency'] for call in recent_calls]
        avg_latency = sum(latencies) / len(latencies)
        
        # Group by model
        models = {}
        for call in recent_calls:
            model = call['model']
            if model not in models:
                models[model] = {
                    'count': 0,
                    'latencies': []
                }
            
            models[model]['count'] += 1
            models[model]['latencies'].append(call['latency'])
        
        # Calculate per-model averages
        for model in models:
            models[model]['avg_latency'] = sum(models[model]['latencies']) / len(models[model]['latencies'])
            # Remove the raw latency list to keep the response smaller
            del models[model]['latencies']
        
        return {
            'count': len(recent_calls),
            'avg_latency': avg_latency,
            'models': models
        }
    
    def get_tool_usage_stats(self, time_range_minutes=None):
        """Get tool usage statistics"""
        # Since we don't track tool usage timestamps, we return all data
        # In a real implementation, you'd want to track timestamps for tools too
        
        # Sort tools by usage count (descending)
        sorted_tools = sorted(
            self.tool_usage.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            'tools': [item[0] for item in sorted_tools],
            'counts': [item[1] for item in sorted_tools],
            'total_usage': sum(self.tool_usage.values())
        }
    
    def get_all_metrics(self, time_range_minutes=60):
        """Get all metrics in a single call"""
        return {
            'memory': self.get_memory_usage(time_range_minutes),
            'agents': self.get_agent_performance(time_range_minutes),
            'llm': self.get_llm_performance(time_range_minutes),
            'tools': self.get_tool_usage_stats()
        }
    
    def save_metrics_snapshot(self):
        """Save current metrics to disk"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"metrics_snapshot_{timestamp}.json"
        filepath = os.path.join(self.metrics_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(self.get_all_metrics(), f, indent=2)
            logger.info(f"Saved metrics snapshot to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving metrics snapshot: {str(e)}")
            return None

# Create a decorator for tracking agent execution time
def track_execution_time(agent_name):
    """Decorator to track execution time of agent methods"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Record the execution time
            metrics = MetricsTracker()
            metrics.record_agent_execution(agent_name, execution_time)
            
            return result
        return wrapper
    return decorator

# Create a decorator for tracking LLM API calls
def track_llm_latency(model_name):
    """Decorator to track LLM API call latency"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            latency = time.time() - start_time
            
            # Extract token information if available
            tokens_in = kwargs.get('max_tokens_to_sample', None)
            tokens_out = getattr(result, 'usage', {}).get('completion_tokens', None)
            
            # Record the latency
            metrics = MetricsTracker()
            metrics.record_llm_latency(model_name, latency, tokens_in, tokens_out)
            
            return result
        return wrapper
    return decorator

# Create a decorator for tracking tool usage
def track_tool_usage(tool_name):
    """Decorator to track tool usage"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Record the tool usage before execution
            metrics = MetricsTracker()
            metrics.record_tool_usage(tool_name)
            
            # Execute the tool
            return func(*args, **kwargs)
        return wrapper
    return decorator 