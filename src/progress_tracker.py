"""Progress tracker for scanning and TMDB operations."""

import threading
from typing import Optional, Dict

class ProgressTracker:
    """Singleton progress tracker for monitoring scan operations."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._progress = {
            'active': False,
            'stage': '',
            'current': 0,
            'total': 0,
            'current_item': '',
            'message': ''
        }
        self._lock = threading.Lock()
    
    def start(self, stage: str, total: int = 0, message: str = ''):
        """Start a new progress tracking stage."""
        with self._lock:
            self._progress = {
                'active': True,
                'stage': stage,
                'current': 0,
                'total': total,
                'current_item': '',
                'message': message
            }
    
    def update(self, current: int = None, current_item: str = None, message: str = None, total: int = None):
        """Update progress information."""
        with self._lock:
            if current is not None:
                self._progress['current'] = current
            if current_item is not None:
                self._progress['current_item'] = current_item
            if message is not None:
                self._progress['message'] = message
            if total is not None:
                self._progress['total'] = total
    
    def increment(self, current_item: str = None):
        """Increment current progress by 1."""
        with self._lock:
            self._progress['current'] += 1
            if current_item is not None:
                self._progress['current_item'] = current_item
    
    def finish(self, message: str = 'Dokončeno'):
        """Mark progress as finished."""
        with self._lock:
            self._progress['active'] = False
            self._progress['message'] = message
            self._progress['current'] = self._progress['total']
    
    def get_progress(self) -> Dict:
        """Get current progress snapshot."""
        with self._lock:
            return self._progress.copy()
    
    def reset(self):
        """Reset progress to initial state."""
        with self._lock:
            self._progress = {
                'active': False,
                'stage': '',
                'current': 0,
                'total': 0,
                'current_item': '',
                'message': ''
            }
