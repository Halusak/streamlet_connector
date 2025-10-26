import os
import re
import sys
from typing import List, Dict, Optional
from src.progress_tracker import ProgressTracker

class MediaScanner:
    """Scanner for movies and TV shows in specified folders."""

    VIDEO_EXTENSIONS = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
    # Common folder names indicating seasons (multi-language)
    SEASON_DIR_PATTERN = re.compile(r"^(?:s(?:eason)?\s*|sez(?:ona|óna)\s*|serie\s*|series\s*|saison\s*)(\d{1,3})$",
                                    re.IGNORECASE)
    # Episode filename patterns: S01E02, 1x02, s1 e2, season 1 episode 2
    EPISODE_PATTERNS = [
        re.compile(r"[sS](\d{1,2})[\W_]*[eE](\d{1,2})"),
        re.compile(r"(\d{1,2})\s*[xX]\s*(\d{1,2})"),
        re.compile(r"season\s*(\d{1,2})\D*episode\s*(\d{1,2})", re.IGNORECASE),
        re.compile(r"\b(\d{1,2})\s*\.\s*(\d{1,2})\b")  # e.g., 1.02
    ]

    def __init__(self, folders: List[str]):
        self.folders = []
        self.progress = ProgressTracker()
        for f in folders:
            # Normalize path based on OS
            normalized = self._normalize_path(f)
            self.folders.append(normalized)
            print(f"[Scanner] Added folder: {normalized}")

    def _normalize_path(self, path: str) -> str:
        """Normalize path for current OS."""
        if sys.platform == 'win32':
            # On Windows, convert UNC paths properly
            if path.startswith('//'):
                # Unix-style UNC: //host/share -> \\host\share
                path = '\\\\' + path[2:].replace('/', '\\')
            elif path.startswith('/'):
                # Single slash path, convert to backslash
                path = path.replace('/', '\\')
            # If already has backslashes, leave as is
        else:
            # On Linux/Mac, convert to forward slashes
            path = path.replace('\\', '/')
        
        return path

    def scan(self) -> List[Dict]:
        """Scan folders and return list of media items."""
        media_items = []
        
        self.progress.start('scanning', len(self.folders), 'Skenování složek...')
        
        for idx, folder_path in enumerate(self.folders):
            self.progress.update(current=idx, current_item=folder_path)
            print(f"\n[Scanner] Starting scan of: {folder_path}")
            
            try:
                # Verify folder exists and is accessible
                if not os.path.exists(folder_path):
                    print(f"[Scanner] ERROR: Folder does not exist: {folder_path}")
                    continue
                
                if not os.path.isdir(folder_path):
                    print(f"[Scanner] ERROR: Path is not a directory: {folder_path}")
                    continue
                
                # Test accessibility
                try:
                    contents = os.listdir(folder_path)
                    print(f"[Scanner] Folder accessible, contains {len(contents)} items")
                except PermissionError as e:
                    print(f"[Scanner] ERROR: Permission denied: {e}")
                    continue
                except Exception as e:
                    print(f"[Scanner] ERROR: Cannot list directory: {e}")
                    continue
                
                # Scan the folder
                found = self._scan_folder(folder_path)
                print(f"[Scanner] Found {len(found)} media items in this folder")
                media_items.extend(found)
                
            except Exception as e:
                print(f"[Scanner] ERROR scanning {folder_path}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n[Scanner] Total media items found: {len(media_items)}")
        self.progress.finish(f'Nalezeno {len(media_items)} položek')
        return media_items

    def _scan_folder(self, folder: str) -> List[Dict]:
        """Recursively scan a folder for media files."""
        items = []
        
        try:
            # Walk through directory tree
            for root, dirs, files in os.walk(folder):
                # Check if this looks like a TV show folder (has Season-like folders)
                season_dirs = [d for d in dirs if self.SEASON_DIR_PATTERN.search(d) or re.search(r"^s\d{1,3}$", d, re.IGNORECASE)]
                
                if season_dirs:
                    # This is a TV show folder
                    print(f"[Scanner] Found TV show folder: {root}")
                    tv_show = self._parse_tv_show(root, dirs)
                    if tv_show:
                        items.append(tv_show)
                    # Don't recurse into season folders
                    dirs[:] = []
                else:
                    # Detect if directory contains TV episodes by filename
                    episode_files = []
                    for filename in files:
                        season_ep = self._extract_episode_info(filename)
                        if season_ep is not None:
                            season_num, ep_num = season_ep
                            _, ext = os.path.splitext(filename)
                            if ext.lower() in self.VIDEO_EXTENSIONS:
                                episode_files.append((season_num, ep_num, filename))

                    if len(episode_files) >= 2:
                        # Heuristic: if 2+ episode files, treat as TV show folder
                        print(f"[Scanner] Detected TV show by episode filenames: {root}")
                        show = self._build_tv_show_from_files(root, episode_files)
                        if show:
                            items.append(show)
                        # Do not descend further from here for this root
                        dirs[:] = []
                    else:
                        # Look for movie files in this directory
                        for filename in files:
                            _, ext = os.path.splitext(filename)
                            if ext.lower() in self.VIDEO_EXTENSIONS:
                                file_path = os.path.join(root, filename)
                                movie = self._parse_movie(file_path)
                                if movie:
                                    items.append(movie)
                                    print(f"[Scanner] Found movie: {movie['title']}")
        
        except Exception as e:
            print(f"[Scanner] Error walking directory {folder}: {e}")
        
        return items

    def _extract_episode_info(self, filename: str) -> Optional[tuple]:
        """Try to extract (season, episode) from a filename using common patterns."""
        try:
            name = os.path.splitext(filename)[0]
            for pattern in self.EPISODE_PATTERNS:
                m = pattern.search(name)
                if m:
                    s, e = m.groups()
                    return int(s), int(e)
        except Exception:
            pass
        return None

    def _build_tv_show_from_files(self, folder_path: str, episode_files: List[tuple]) -> Optional[Dict]:
        """Build a tv_show item from a flat folder containing episode files."""
        try:
            folder_name = os.path.basename(folder_path)
            show_name = re.sub(r'\s*\(?\d{4}\)?$', '', folder_name).strip()

            seasons_map: Dict[int, List[Dict]] = {}
            for season_num, ep_num, filename in episode_files:
                ep_list = seasons_map.setdefault(season_num, [])
                ep_list.append({
                    'season': season_num,
                    'episode': ep_num,
                    'path': os.path.join(folder_path, filename),
                    'filename': filename
                })

            seasons = []
            for s in sorted(seasons_map.keys()):
                # sort episodes by episode number
                eps = sorted(seasons_map[s], key=lambda x: x['episode'])
                seasons.append({'season': s, 'episodes': eps})

            if seasons:
                return {
                    'type': 'tv_show',
                    'title': show_name,
                    'path': folder_path,
                    'seasons': seasons
                }
        except Exception as e:
            print(f"[Scanner] Error building TV show from files in {folder_path}: {e}")
        return None

    def _parse_movie(self, file_path: str) -> Optional[Dict]:
        """Parse movie information from file path."""
        try:
            filename = os.path.basename(file_path)
            name_without_ext = os.path.splitext(filename)[0]
            
            # Try to extract title and year
            # Pattern: "Movie Name (2020)" or "Movie Name 2020"
            year_match = re.search(r'\((\d{4})\)|\s(\d{4})(?:\s|$)', name_without_ext)
            
            if year_match:
                year = year_match.group(1) or year_match.group(2)
                # Remove year from title
                title = re.sub(r'\s*\(?\d{4}\)?', '', name_without_ext).strip()
            else:
                title = name_without_ext
                year = None
            
            # Clean up title (remove common artifacts)
            title = re.sub(r'\[.*?\]', '', title)  # Remove [tags]
            title = re.sub(r'\(.*?\)', '', title)  # Remove (tags)
            title = re.sub(r'\s+', ' ', title).strip()  # Normalize whitespace
            
            return {
                'type': 'movie',
                'title': title,
                'year': year,
                'path': file_path,
                'filename': filename
            }
        except Exception as e:
            print(f"[Scanner] Error parsing movie {file_path}: {e}")
            return None

    def _parse_tv_show(self, folder_path: str, subdirs: List[str]) -> Optional[Dict]:
        """Parse TV show information from folder structure."""
        try:
            folder_name = os.path.basename(folder_path)
            
            # Extract show name (remove year if present)
            show_name = re.sub(r'\s*\(?\d{4}\)?$', '', folder_name).strip()
            
            seasons = []
            
            # Find season folders (support multiple naming variants)
            for subdir in subdirs:
                season_match = self.SEASON_DIR_PATTERN.search(subdir) or re.search(r'^s(\d{1,3})$', subdir, re.IGNORECASE)
                if season_match:
                    season_num = int(season_match.group(1))
                    season_path = os.path.join(folder_path, subdir)
                    
                    episodes = []
                    try:
                        for filename in os.listdir(season_path):
                            _, ext = os.path.splitext(filename)
                            if ext.lower() in self.VIDEO_EXTENSIONS:
                                file_path = os.path.join(season_path, filename)
                                
                                # Try to extract episode info from filename
                                ep_info = self._extract_episode_info(filename)
                                if ep_info:
                                    s, e = ep_info
                                    # If season not in filename, fallback to folder season
                                    if s is None:
                                        s = season_num
                                    episodes.append({
                                        'season': s,
                                        'episode': e,
                                        'path': file_path,
                                        'filename': filename
                                    })
                    except Exception as e:
                        print(f"[Scanner] Error reading season folder {season_path}: {e}")
                    
                    if episodes:
                        seasons.append({
                            'season': season_num,
                            'episodes': episodes
                        })
            
            if seasons:
                return {
                    'type': 'tv_show',
                    'title': show_name,
                    'path': folder_path,
                    'seasons': seasons
                }
            
        except Exception as e:
            print(f"[Scanner] Error parsing TV show {folder_path}: {e}")
        
        return None

    def scan_with_metadata(self, tmdb_client, database=None) -> List[Dict]:
        """Scan folders and enrich with TMDB metadata, downloading images immediately."""
        print("[Scanner] Starting scan with TMDB metadata enrichment...")
        items = self.scan()
        
        print(f"[Scanner] Enriching {len(items)} items with TMDB data...")
        # Calculate total work units: each item + each episode
        episode_count = 0
        for it in items:
            if it.get('type') == 'tv_show':
                for season in it.get('seasons', []) or []:
                    episode_count += len(season.get('episodes', []) or [])
        total_units = len(items) + episode_count
        self.progress.start('tmdb', total_units, 'Získávání metadat z TMDB...')
        
        enriched_items = []
        for idx, item in enumerate(items):
            # Announce current item
            self.progress.update(current_item=item.get('title', 'Neznámý'))
            try:
                if item['type'] == 'movie':
                    year = int(item['year']) if item.get('year') else None
                    metadata = tmdb_client.search_movie(item['title'], year)
                    if metadata:
                        item['metadata'] = metadata
                        print(f"[Scanner] Found TMDB data for movie: {item['title']}")
                        
                        # Download images immediately if database provided
                        if database:
                            self.progress.update(message=f'Stahuji data pro: {item["title"]}')
                            database.enrich_with_images(item)
                            # Save to database immediately
                            database.add_or_update(item)
                            database.save()
                    # Count this movie as one unit of work (metadata + images)
                    self.progress.increment(current_item=item.get('title', 'Neznámý'))
                            
                elif item['type'] == 'tv_show':
                    metadata = tmdb_client.search_tv_show(item['title'])
                    if metadata:
                        item['metadata'] = metadata
                        print(f"[Scanner] Found TMDB data for TV show: {item['title']}")
                        
                        # Download show poster/backdrop and save
                        if database:
                            self.progress.update(message=f'Stahuji data pro: {item["title"]}')
                            database.enrich_with_images(item)
                            database.add_or_update(item)
                            database.save()
                        # Count show-level enrichment as one unit
                        self.progress.increment(current_item=item.get('title', 'Neznámý'))

                        # Enrich episodes with TMDB details and still images
                        show_id = metadata.get('id')
                        if show_id and database:
                            for season in item.get('seasons', []):
                                s_no = season.get('season')
                                for ep in season.get('episodes', []):
                                    e_no = ep.get('episode')
                                    if s_no is None or e_no is None:
                                        continue
                                    try:
                                        label = f"{item['title']} S{int(s_no):02}E{int(e_no):02}"
                                        self.progress.update(current_item=label, message=f'Stahuji data pro: {label}')
                                        ep_meta = tmdb_client.get_tv_episode_details(show_id, int(s_no), int(e_no))
                                        if ep_meta:
                                            ep['metadata'] = ep_meta
                                            # set human friendly name
                                            if ep_meta.get('name'):
                                                ep['name'] = ep_meta['name']
                                            # download still image
                                            still_path = ep_meta.get('still_path')
                                            if still_path:
                                                local_still = database.download_episode_still(still_path, show_id, int(s_no), int(e_no))
                                                if local_still:
                                                    ep['local_still_path'] = local_still
                                        # Save progressively to avoid losing progress on long scans
                                        database.add_or_update(item)
                                        database.save()
                                        # Count this episode unit
                                        self.progress.increment(current_item=label)
                                    except Exception as err:
                                        print(f"[Scanner] Episode enrich failed S{s_no}E{e_no}: {err}")
                                        # Even on failure, mark progress for this episode to avoid stalling
                                        self.progress.increment(current_item=f"{item['title']} S{int(s_no):02}E{int(e_no):02}")
                            
            except Exception as e:
                print(f"[Scanner] Error fetching TMDB data for {item.get('title')}: {e}")
            
            enriched_items.append(item)
        
        self.progress.finish(f'Obohaceno {len(items)} položek')
        return enriched_items
