import json
import os
import requests
from pathlib import Path
from typing import Dict, List, Optional
import hashlib

class MediaDatabase:
    """Manages persistent storage of scanned media with metadata and images."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / 'data' / 'media_db.json'
        
        self.db_path = Path(db_path)
        self.images_dir = self.db_path.parent / 'images'
        
        # Create directories if they don't exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        self.media_items = []
        self.load()
        self._migrate_image_paths()

    def load(self):
        """Load media database from file."""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    self.media_items = json.load(f)
                print(f"[Database] Loaded {len(self.media_items)} items from database")
            except Exception as e:
                print(f"[Database] Error loading database: {e}")
                self.media_items = []
        else:
            self.media_items = []

    def _migrate_image_paths(self):
        """Migrate old absolute image paths to filenames."""
        migrated = False
        for item in self.media_items:
            for key in ['local_poster_path', 'local_backdrop_path']:
                if key in item and item[key]:
                    path = item[key]
                    # Check if it's an absolute path (old format)
                    if os.path.isabs(path):
                        # Convert to just filename
                        filename = os.path.basename(path)
                        item[key] = filename
                        migrated = True
                        print(f"[Database] Migrated {key}: {path} -> {filename}")
        
        if migrated:
            print(f"[Database] Migrated image paths to new format")
            self.save()
    
    def save(self):
        """Save media database to file."""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.media_items, f, indent=2, ensure_ascii=False)
            print(f"[Database] Saved {len(self.media_items)} items to database")
        except Exception as e:
            print(f"[Database] Error saving database: {e}")

    def get_all_items(self) -> List[Dict]:
        """Get all media items from database."""
        return self.media_items.copy()

    def find_by_path(self, path: str) -> Optional[Dict]:
        """Find media item by file path."""
        normalized_path = os.path.normpath(path)
        for item in self.media_items:
            if os.path.normpath(item.get('path', '')) == normalized_path:
                return item
        return None

    def add_or_update(self, item: Dict):
        """Add new item or update existing one."""
        existing = self.find_by_path(item['path'])
        if existing:
            # Update existing item
            index = self.media_items.index(existing)
            self.media_items[index] = item
            print(f"[Database] Updated item: {item.get('title', 'Unknown')}")
        else:
            # Add new item
            self.media_items.append(item)
            print(f"[Database] Added item: {item.get('title', 'Unknown')}")

    def remove(self, path: str):
        """Remove item by path."""
        item = self.find_by_path(path)
        if item:
            self.media_items.remove(item)
            print(f"[Database] Removed item: {item.get('title', 'Unknown')}")
            return True
        return False

    def download_image(self, url: str, tmdb_id: int, image_type: str) -> Optional[str]:
        """
        Download image from TMDB and save locally.
        
        Args:
            url: TMDB image path (e.g., '/abc123.jpg')
            tmdb_id: TMDB ID for organizing images
            image_type: 'poster' or 'backdrop'
        
        Returns:
            Filename (not full path) of downloaded image, or None if failed
        """
        if not url:
            return None

        try:
            # TMDB image base URL
            base_url = "https://image.tmdb.org/t/p/"
            # Use w500 for posters, w1280 for backdrops
            size = "w500" if image_type == "poster" else "w1280"
            full_url = f"{base_url}{size}{url}"

            # Create filename from TMDB ID and original filename
            filename = f"{tmdb_id}_{image_type}_{os.path.basename(url)}"
            local_path = self.images_dir / filename

            # Download if not already cached
            if not local_path.exists():
                print(f"[Database] Downloading {image_type}: {full_url}")
                response = requests.get(full_url, timeout=10)
                response.raise_for_status()
                
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                print(f"[Database] Saved {image_type} to: {local_path}")
            else:
                print(f"[Database] Using cached {image_type}: {local_path}")

            # Return just the filename, not the full path
            return filename
        except Exception as e:
            print(f"[Database] Error downloading image {url}: {e}")
            return None

    def remove_old_images(self, item: Dict):
        """
        Remove old images for an item before downloading new ones.
        
        Args:
            item: Media item dict with potentially old image paths (filenames)
        """
        for key in ['local_poster_path', 'local_backdrop_path']:
            if key in item and item[key]:
                try:
                    # Handle both old absolute paths and new filenames
                    filename = item[key]
                    if os.path.isabs(filename):
                        # Old format: absolute path
                        path = Path(filename)
                    else:
                        # New format: just filename
                        path = self.images_dir / filename
                    
                    if path.exists():
                        path.unlink()
                        print(f"[Database] Deleted old image: {path}")
                except Exception as e:
                    print(f"[Database] Error deleting old image: {e}")
                # Remove the reference
                del item[key]

    def enrich_with_images(self, item: Dict) -> Dict:
        """
        Download and cache images for media item with TMDB metadata.
        
        Args:
            item: Media item dict with 'metadata' containing TMDB data
        
        Returns:
            Updated item with local image paths
        """
        if 'metadata' not in item:
            return item

        metadata = item['metadata']
        tmdb_id = metadata.get('id')
        
        if not tmdb_id:
            return item

        # Download poster
        poster_path = metadata.get('poster_path')
        if poster_path:
            local_poster = self.download_image(poster_path, tmdb_id, 'poster')
            if local_poster:
                item['local_poster_path'] = local_poster

        # Download backdrop
        backdrop_path = metadata.get('backdrop_path')
        if backdrop_path:
            local_backdrop = self.download_image(backdrop_path, tmdb_id, 'backdrop')
            if local_backdrop:
                item['local_backdrop_path'] = local_backdrop

        return item

    def download_episode_still(self, still_path: str, tmdb_show_id: int, season_number: int, episode_number: int) -> Optional[str]:
        """
        Download and save a TV episode still image locally.

        Args:
            still_path: TMDB still image path (e.g., '/abc123.jpg')
            tmdb_show_id: TMDB show ID
            season_number: Season number
            episode_number: Episode number

        Returns:
            Filename of downloaded image in local images dir or None if fails
        """
        if not still_path:
            return None
        try:
            base_url = "https://image.tmdb.org/t/p/"
            size = "w342"
            full_url = f"{base_url}{size}{still_path}"

            filename = f"{tmdb_show_id}_S{int(season_number):02d}E{int(episode_number):02d}_still_{os.path.basename(still_path)}"
            local_path = self.images_dir / filename

            if not local_path.exists():
                print(f"[Database] Downloading episode still: {full_url}")
                response = requests.get(full_url, timeout=10)
                response.raise_for_status()
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                print(f"[Database] Saved episode still to: {local_path}")
            else:
                print(f"[Database] Using cached episode still: {local_path}")

            return filename
        except Exception as e:
            print(f"[Database] Error downloading episode still {still_path}: {e}")
            return None

    def _download_images(self, item: Dict) -> Dict:
        """
        Download and cache images for media item. Called from API after metadata assignment.
        Alias for enrich_with_images to maintain API compatibility.
        """
        return self.enrich_with_images(item)

    def get_new_files(self, scanned_items: List[Dict]) -> List[Dict]:
        """
        Compare scanned items with database to find new files.
        
        Args:
            scanned_items: List of items from scanner
        
        Returns:
            List of items that are not in database
        """
        new_items = []
        for item in scanned_items:
            if not self.find_by_path(item['path']):
                new_items.append(item)
        return new_items

    def mark_missing_files(self, scanned_paths: List[str]):
        """
        Mark database items as missing if they're not in scanned paths.
        
        Args:
            scanned_paths: List of file paths from current scan
        """
        normalized_scanned = [os.path.normpath(p) for p in scanned_paths]
        
        for item in self.media_items:
            item_path = os.path.normpath(item.get('path', ''))
            if item_path not in normalized_scanned:
                item['missing'] = True
                print(f"[Database] Marked as missing: {item.get('title', 'Unknown')}")
            else:
                # Remove missing flag if file is found again
                if 'missing' in item:
                    del item['missing']
                    print(f"[Database] File found again: {item.get('title', 'Unknown')}")

    def clear_all(self) -> bool:
        """
        Clear entire database and delete all downloaded images.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete all images
            if self.images_dir.exists():
                import shutil
                shutil.rmtree(self.images_dir)
                self.images_dir.mkdir(parents=True, exist_ok=True)
                print("[Database] Deleted all images")
            
            # Clear database
            self.media_items = []
            self.save()
            print("[Database] Database cleared")
            return True
        except Exception as e:
            print(f"[Database] Error clearing database: {e}")
            return False
    
    def remove_missing_files(self) -> int:
        """
        Remove items from database that no longer exist on disk.
        
        Returns:
            Number of items removed
        """
        removed_count = 0
        items_to_keep = []
        
        for item in self.media_items:
            path = item.get('path')
            if path and os.path.exists(path):
                items_to_keep.append(item)
            else:
                print(f"[Database] Removing missing file: {item.get('title', 'Unknown')} - {path}")
                removed_count += 1
        
        self.media_items = items_to_keep
        if removed_count > 0:
            self.save()
        
        return removed_count

    def add_item(self, item: Dict):
        """Add new item to database (alias for compatibility)."""
        self.add_or_update(item)
