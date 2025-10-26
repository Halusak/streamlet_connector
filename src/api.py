from flask import Flask, request, jsonify, send_file, render_template_string, send_from_directory, Response
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from src.media_database import MediaDatabase
from src.scanner import MediaScanner
from src.tmdb_client import TMDBClient
from src.progress_tracker import ProgressTracker
import mimetypes

# Ensure common video mime types are known (Windows mimetypes may miss some)
mimetypes.add_type('video/mp4', '.mp4')
mimetypes.add_type('video/x-m4v', '.m4v')
mimetypes.add_type('video/webm', '.webm')
mimetypes.add_type('video/x-matroska', '.mkv')
mimetypes.add_type('video/x-msvideo', '.avi')
mimetypes.add_type('video/quicktime', '.mov')
mimetypes.add_type('video/x-ms-wmv', '.wmv')
mimetypes.add_type('video/x-flv', '.flv')

class CustomAPI:
    """Custom API to serve media data and files."""

    def __init__(self, host: str = 'localhost', port: int = 5000, database: MediaDatabase = None):
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.database = database or MediaDatabase()
        self.config = self._load_config()
        self.scanner = MediaScanner(self.config.get('folders_to_scan', []))
        self.tmdb_client = TMDBClient(
            self.config.get('tmdb_api_key', ''),
            self.config.get('tmdb_language', 'cs-CZ')
        )
        self.progress = ProgressTracker()
        self._setup_routes()
    
    def _load_config(self) -> Dict:
        """Load configuration from file."""
        config_path = Path(__file__).parent.parent / 'config' / 'config.json'
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'folders_to_scan': [],
                'tmdb_api_key': '',
                'tmdb_language': 'cs-CZ',
                'custom_api_url': '',
                'scan_interval': 3600
            }
    
    def _save_config(self, config: Dict) -> bool:
        """Save configuration to file."""
        config_path = Path(__file__).parent.parent / 'config' / 'config.json'
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[API] Error saving config: {e}")
            return False

    def _get_image_url(self, local_path: str) -> Optional[str]:
        """Convert local image filename to URL path."""
        if not local_path:
            return None
        
        # If it already starts with /, it's a TMDB path that wasn't downloaded - skip it
        if local_path.startswith('/'):
            return None
        
        # Extract just the filename from absolute path (legacy compatibility)
        filename = os.path.basename(local_path)
        return filename

    def _setup_routes(self):
        """Setup all API routes."""
        
        # ========== WEB UI ==========
        @self.app.route('/ui', methods=['GET'])
        @self.app.route('/', methods=['GET'])
        def web_ui():
            """Serve main web UI."""
            return render_template_string(self._get_web_ui_html())
        
        # ========== API: DATABASE ==========
        @self.app.route('/api/items', methods=['GET'])
        def get_all_items():
            """Get all items including those without metadata."""
            items = []
            for idx, item in enumerate(self.database.get_all_items()):
                item_data = {
                    'internal_id': idx,
                    'path': item.get('path'),
                    'title': item.get('title', 'Unknown'),
                    'type': item.get('type'),
                    'has_metadata': 'metadata' in item and item['metadata'] is not None
                }
                
                if item_data['has_metadata']:
                    metadata = item['metadata']
                    item_data.update({
                        'tmdb_id': metadata.get('id'),
                        'display_title': metadata.get('title') or metadata.get('name', item_data['title']),
                        'poster_path': self._get_image_url(metadata.get('poster_path')),
                        'backdrop_path': self._get_image_url(metadata.get('backdrop_path')),
                        'rating': metadata.get('vote_average', 0),
                        'year': (metadata.get('release_date') or metadata.get('first_air_date', ''))[:4],
                        'overview': metadata.get('overview', '')
                    })
                else:
                    item_data['display_title'] = item_data['title']
                
                items.append(item_data)
            
            return jsonify(items), 200
        
        # ========== API: LOCAL SEARCH ==========
        @self.app.route('/api/search', methods=['GET'])
        def search_local():
            """Search local database for movies or TV shows."""
            query = request.args.get('query', '').strip().lower()
            media_type = request.args.get('type', 'movie')  # 'movie' or 'tv'
            
            if not query:
                return jsonify({'error': 'Query parameter required'}), 400
            
            if media_type not in ['movie', 'tv']:
                return jsonify({'error': 'Type must be movie or tv'}), 400
            
            try:
                results = []
                target_type = 'movie' if media_type == 'movie' else 'tv_show'
                
                for item in self.database.get_all_items():
                    if item.get('type') != target_type or 'metadata' not in item:
                        continue
                    
                    metadata = item['metadata']
                    title = (metadata.get('title') or metadata.get('name', '')).lower()
                    overview = (metadata.get('overview', '')).lower()
                    
                    # Search in title and overview
                    if query in title or query in overview:
                        results.append({
                            'id': metadata.get('id'),
                            'title': metadata.get('title') or metadata.get('name'),
                            'year': (metadata.get('release_date') or metadata.get('first_air_date', ''))[:4],
                            'overview': metadata.get('overview', ''),
                            'poster_path': self._get_image_url(metadata.get('poster_path')),
                            'rating': metadata.get('vote_average', 0)
                        })
                
                # Limit to 10 results
                return jsonify(results[:10]), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # ========== API: ASSIGN METADATA ==========
        @self.app.route('/api/assign-metadata', methods=['POST'])
        def assign_metadata():
            """Assign TMDB metadata to an item."""
            data = request.get_json()
            internal_id = data.get('internal_id')
            tmdb_id = data.get('tmdb_id')
            media_type = data.get('type')
            
            if internal_id is None or tmdb_id is None or not media_type:
                return jsonify({'error': 'internal_id, tmdb_id and type required'}), 400
            
            if internal_id < 0 or internal_id >= len(self.database.media_items):
                return jsonify({'error': 'Invalid internal_id'}), 404
            
            try:
                # Get item reference
                item = self.database.media_items[internal_id]
                
                # Remove old images if replacing metadata
                if item.get('metadata'):
                    print(f"[API] Replacing metadata for: {item.get('title', 'Unknown')}")
                    self.database.remove_old_images(item)
                
                # Fetch metadata from TMDB
                if media_type == 'movie':
                    metadata = self.tmdb_client.get_movie_details(tmdb_id)
                elif media_type == 'tv_show' or media_type == 'tv':
                    metadata = self.tmdb_client.get_tv_show_details(tmdb_id)
                else:
                    return jsonify({'error': 'Invalid type'}), 400
                
                # Update item with new metadata
                item['metadata'] = metadata
                item['type'] = 'movie' if media_type == 'movie' else 'tv_show'
                
                # Download new images
                self.database.enrich_with_images(item)
                
                # Save to database
                self.database.save()
                
                return jsonify({'success': True, 'message': 'Metadata assigned successfully'}), 200
            except Exception as e:
                import traceback
                traceback.print_exc()
                return jsonify({'error': str(e)}), 500
        
        # ========== API: SETTINGS ==========
        @self.app.route('/api/settings', methods=['GET'])
        def get_settings():
            """Get current settings."""
            return jsonify(self.config), 200
        
        @self.app.route('/api/settings', methods=['POST'])
        def save_settings():
            """Save settings."""
            data = request.get_json()
            
            # Update config
            if 'folders_to_scan' in data:
                self.config['folders_to_scan'] = data['folders_to_scan']
            if 'tmdb_api_key' in data:
                self.config['tmdb_api_key'] = data['tmdb_api_key']
                self.tmdb_client.api_key = data['tmdb_api_key']
            if 'tmdb_language' in data:
                self.config['tmdb_language'] = data['tmdb_language']
                self.tmdb_client.language = data['tmdb_language']
            if 'custom_api_url' in data:
                self.config['custom_api_url'] = data['custom_api_url']
            if 'scan_interval' in data:
                self.config['scan_interval'] = data['scan_interval']
            
            # Save to file
            if self._save_config(self.config):
                # Update scanner with new folders
                self.scanner = MediaScanner(self.config.get('folders_to_scan', []))
                return jsonify({'success': True, 'message': 'Settings saved'}), 200
            else:
                return jsonify({'error': 'Failed to save settings'}), 500
        
        # ========== API: SCAN ==========
        @self.app.route('/api/scan', methods=['POST'])
        def start_scan():
            """Start media scan, enrich with TMDB, and remove missing files."""
            try:
                # Scan folders with metadata enrichment and immediate save
                if self.tmdb_client and self.tmdb_client.movie_api and self.tmdb_client.tv_api:
                    # Pass database to scanner for immediate saves
                    items = self.scanner.scan_with_metadata(self.tmdb_client, self.database)
                else:
                    items = self.scanner.scan()
                
                # Remove files that no longer exist
                removed_count = self.database.remove_missing_files()
                
                # Count new vs updated items
                existing_paths = {item['path'] for item in self.database.get_all_items()}
                new_count = sum(1 for item in items if item['path'] not in existing_paths)
                enriched_count = sum(1 for item in items if item.get('metadata'))
                
                # Items without metadata still need to be added
                for item in items:
                    if item['path'] not in existing_paths and not item.get('metadata'):
                        self.database.add_or_update(item)
                
                # Final save
                self.database.save()
                
                return jsonify({
                    'success': True,
                    'total_found': len(items),
                    'new_items': new_count,
                    'removed_items': removed_count,
                    'enriched_with_metadata': enriched_count,
                    'message': f'Found {len(items)} items, added {new_count} new, removed {removed_count} missing'
                }), 200
            except Exception as e:
                import traceback
                traceback.print_exc()
                return jsonify({'error': str(e)}), 500
        
        # ========== API: PROGRESS ==========
        @self.app.route('/api/progress', methods=['GET'])
        def get_progress():
            """Get current scan progress."""
            return jsonify(self.progress.get_progress()), 200
        
        # ========== API: DATABASE MANAGEMENT ==========
        @self.app.route('/api/database/clear', methods=['POST'])
        def clear_database():
            """Clear entire database and all images."""
            try:
                if self.database.clear_all():
                    return jsonify({'success': True, 'message': 'Database and images cleared'}), 200
                else:
                    return jsonify({'error': 'Failed to clear database'}), 500
            except Exception as e:
                return jsonify({'error': str(e)}), 500
                
                for item in items:
                    if item['path'] not in existing_paths:
                        self.database.add_item(item)
                        new_count += 1
                
                self.database.save()
                
                return jsonify({
                    'success': True,
                    'total_found': len(items),
                    'new_items': new_count,
                    'message': f'Found {len(items)} items, added {new_count} new'
                }), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # ========== API: IMAGES ==========
        @self.app.route('/api/images/<path:filename>', methods=['GET'])
        def get_image(filename):
            """Serve local images."""
            images_dir = Path(__file__).parent.parent / 'data' / 'images'
            try:
                return send_from_directory(images_dir, filename)
            except Exception as e:
                return jsonify({'error': 'Image not found'}), 404
        
        # ========== API: MOVIES ==========
        @self.app.route('/api/movies', methods=['GET'])
        def get_movies():
            """Get all movies with basic info: id, title, poster, rating."""
            movies = []
            for item in self.database.get_all_items():
                if item.get('type') == 'movie' and 'metadata' in item:
                    metadata = item['metadata']
                    movies.append({
                        'id': metadata.get('id'),
                        'title': metadata.get('title', item.get('title', 'Unknown')),
                        'poster_path': self._get_image_url(metadata.get('poster_path')),
                        'rating': metadata.get('vote_average', 0)
                    })
            return jsonify(movies), 200

        # ========== API: TV SHOWS ==========
        @self.app.route('/api/tv-shows', methods=['GET'])
        def get_tv_shows():
            """Get all TV shows with basic info: id, title, poster, rating."""
            tv_shows = []
            for item in self.database.get_all_items():
                if item.get('type') == 'tv_show' and 'metadata' in item:
                    metadata = item['metadata']
                    tv_shows.append({
                        'id': metadata.get('id'),
                        'title': metadata.get('name', item.get('title', 'Unknown')),
                        'poster_path': self._get_image_url(metadata.get('poster_path')),
                        'rating': metadata.get('vote_average', 0)
                    })
            return jsonify(tv_shows), 200

        # ========== API: MOVIE DETAIL ==========
        @self.app.route('/api/movie/<int:tmdb_id>', methods=['GET'])
        def get_movie_details(tmdb_id):
            """Get complete movie details by TMDB ID."""
            for item in self.database.get_all_items():
                if item.get('type') == 'movie' and 'metadata' in item:
                    if item['metadata'].get('id') == tmdb_id:
                        result = item['metadata'].copy()
                        # Add file info
                        result['file_path'] = item.get('path')
                        result['year'] = item.get('year')
                        # Add internal ID for stream access
                        result['internal_id'] = self._get_item_internal_id(item)
                        return jsonify(result), 200
            return jsonify({'error': 'Movie not found'}), 404

        # ========== API: SERIES DETAIL ==========
        @self.app.route('/api/tv-show/<int:tmdb_id>', methods=['GET'])
        def get_tv_show_details(tmdb_id):
            """Get complete TV show details by TMDB ID."""
            for item in self.database.get_all_items():
                if item.get('type') == 'tv_show' and 'metadata' in item:
                    if item['metadata'].get('id') == tmdb_id:
                        result = item['metadata'].copy()
                        # Add file info
                        result['file_path'] = item.get('path')
                        result['seasons'] = item.get('seasons', [])
                        # Add internal ID for stream access
                        result['internal_id'] = self._get_item_internal_id(item)
                        return jsonify(result), 200
            return jsonify({'error': 'TV show not found'}), 404

        # ========== API: SERIES EPISODE DETAIL ==========
        @self.app.route('/api/tv-show/<int:tmdb_id>/season/<int:season_number>/episode/<int:episode_number>', methods=['GET'])
        def get_tv_episode_details(tmdb_id, season_number, episode_number):
            """Get details about a specific TV episode (mirrors TMDB style), augmented with local file info if available."""
            # Try to locate the TV show in local DB to enrich with local episode path
            local_item = None
            for item in self.database.get_all_items():
                if item.get('type') == 'tv_show' and 'metadata' in item and item['metadata'].get('id') == tmdb_id:
                    local_item = item
                    break

            # Fetch TMDB episode details if possible
            episode_meta = self.tmdb_client.get_tv_episode_details(tmdb_id, season_number, episode_number)

            response_data = episode_meta or {}
            response_data.setdefault('season_number', int(season_number))
            response_data.setdefault('episode_number', int(episode_number))
            response_data['tmdb_show_id'] = tmdb_id

            # Attach local file info when present
            found_local = False
            if local_item:
                for season in local_item.get('seasons', []):
                    if int(season.get('season')) == int(season_number):
                        for ep in season.get('episodes', []):
                            if int(ep.get('episode')) == int(episode_number):
                                response_data['local_path'] = ep.get('path')
                                response_data['filename'] = ep.get('filename')
                                response_data['stream_available'] = os.path.exists(ep.get('path')) if ep.get('path') else False
                                found_local = True
                                break
            if not episode_meta and not found_local:
                return jsonify({'error': 'Episode not found'}), 404
            return jsonify(response_data), 200

        # ========== API: SERIES SEASON DETAIL ==========
        @self.app.route('/api/tv-show/<int:tmdb_id>/season/<int:season_number>', methods=['GET'])
        @self.app.route('/api/tv/<int:tmdb_id>/season/<int:season_number>', methods=['GET'])
        def get_tv_season(tmdb_id, season_number):
            """Get all episodes for a TV season with normalized fields and local stream info where available."""
            try:
                episodes = self.tmdb_client.get_tv_season_episodes(tmdb_id, season_number) if self.tmdb_client else []

                # Merge local info if show exists in DB
                local_item = None
                for item in self.database.get_all_items():
                    if item.get('type') == 'tv_show' and 'metadata' in item and item['metadata'].get('id') == tmdb_id:
                        local_item = item
                        break

                if local_item:
                    local_lookup = {}
                    for season in local_item.get('seasons', []):
                        if int(season.get('season')) == int(season_number):
                            for ep in season.get('episodes', []):
                                key = int(ep.get('episode')) if ep.get('episode') is not None else None
                                if key is not None:
                                    local_lookup[key] = ep
                    # Attach local info to matching episode numbers
                    for ep in episodes:
                        ep_no = int(ep.get('episode_number')) if ep.get('episode_number') is not None else None
                        if ep_no in local_lookup:
                            lep = local_lookup[ep_no]
                            ep['local_path'] = lep.get('path')
                            ep['filename'] = lep.get('filename')
                            ep['stream_available'] = os.path.exists(lep.get('path')) if lep.get('path') else False
                            # Prefer local stored metadata name if present
                            name_local = (lep.get('metadata') or {}).get('name') or lep.get('name')
                            if name_local:
                                ep['name'] = name_local
                            # Attach local still if available
                            if lep.get('still_path'):
                                ep['still_path'] = lep.get('still_path')

                return jsonify({ 'episodes': episodes }), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        # ========== API: SERIES STREAM DETAIL ==========
        @self.app.route('/api/tv-show/<int:tmdb_id>/season/<int:season_number>/episode/<int:episode_number>/stream', methods=['GET'])
        @self.app.route('/api/tv/<int:tmdb_id>/season/<int:season_number>/episode/<int:episode_number>/stream', methods=['GET'])
        def stream_tv_episode(tmdb_id, season_number, episode_number):
            """Stream a local episode file if available."""
            try:
                for item in self.database.get_all_items():
                    if item.get('type') == 'tv_show' and 'metadata' in item and item['metadata'].get('id') == tmdb_id:
                        for season in item.get('seasons', []):
                            if int(season.get('season')) == int(season_number):
                                for ep in season.get('episodes', []):
                                    if int(ep.get('episode')) == int(episode_number):
                                        path = ep.get('path')
                                        if path and os.path.exists(path):
                                            return self._send_partial_file(path)
                                        return jsonify({'error': 'File not found'}), 404
                return jsonify({'error': 'Episode not found'}), 404
            except Exception as e:
                return jsonify({'error': f'Failed to send file: {str(e)}'}), 500

        # ========== API: STREAMS ==========
        @self.app.route('/api/streams', methods=['GET'])
        def get_streams():
            """Get list of all video files (streams) with TMDB ID, name, type, size."""
            streams = []
            for item in self.database.get_all_items():
                file_path = item.get('path')
                if file_path and os.path.exists(file_path) and 'metadata' in item:
                    metadata = item['metadata']
                    tmdb_id = metadata.get('id')
                    if tmdb_id:
                        file_stat = os.stat(file_path)
                        file_ext = os.path.splitext(file_path)[1].lower()
                        streams.append({
                            'id': tmdb_id,  # TMDB ID
                            'name': os.path.basename(file_path),
                            'type': file_ext.replace('.', ''),
                            'size': file_stat.st_size,
                            'title': metadata.get('title') or metadata.get('name', 'Unknown'),
                            'media_type': item.get('type')
                        })
            return jsonify(streams), 200

        # ========== API: STREAM BY TMDB ID ==========
        @self.app.route('/api/stream/<int:tmdb_id>', methods=['GET'])
        def get_stream_file(tmdb_id):
            """Get direct link/file for stream by TMDB ID."""
            for item in self.database.get_all_items():
                if 'metadata' in item and item['metadata'].get('id') == tmdb_id:
                    file_path = item.get('path')
                    
                    if not file_path or not os.path.exists(file_path):
                        return jsonify({'error': 'File not found'}), 404
                    
                    try:
                        # Return the actual file for streaming with Range support
                        return self._send_partial_file(file_path)
                    except Exception as e:
                        return jsonify({'error': f'Failed to send file: {str(e)}'}), 500
            
            return jsonify({'error': 'Stream not found'}), 404

        # ========== API: STREAM INFO ==========
        @self.app.route('/api/stream/<int:tmdb_id>/info', methods=['GET'])
        def get_stream_info(tmdb_id):
            """Get stream file information by TMDB ID without downloading."""
            for item in self.database.get_all_items():
                if 'metadata' in item and item['metadata'].get('id') == tmdb_id:
                    file_path = item.get('path')
                    
                    if not file_path or not os.path.exists(file_path):
                        return jsonify({'error': 'File not found'}), 404
                    
                    file_stat = os.stat(file_path)
                    return jsonify({
                        'id': tmdb_id,
                        'path': file_path,
                        'name': os.path.basename(file_path),
                        'type': os.path.splitext(file_path)[1].replace('.', ''),
                        'size': file_stat.st_size,
                        'url': f'{self.config['custom_api_url']}/api/stream/{tmdb_id}'
                    }), 200
            
            return jsonify({'error': 'Stream not found'}), 404

        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            return jsonify({
                'status': 'ok',
                'total_items': len(self.database.get_all_items()),
                'movies': len([i for i in self.database.get_all_items() if i.get('type') == 'movie']),
                'tv_shows': len([i for i in self.database.get_all_items() if i.get('type') == 'tv_show'])
            }), 200

    def _get_item_internal_id(self, item: Dict) -> Optional[int]:
        """Get internal ID (index) of item in database."""
        items = self.database.get_all_items()
        try:
            return items.index(item)
        except ValueError:
            return None

    def send_media_data(self, media_data: Dict, target_url: str):
        """Send media data to external API."""
        import requests
        try:
            response = requests.post(target_url, json=media_data)
            response.raise_for_status()
            print(f"Successfully sent data to {target_url}")
        except requests.RequestException as e:
            print(f"Failed to send data: {e}")
    
    def _get_web_ui_html(self) -> str:
        """Generate main web UI HTML."""
        # Due to length, this will be loaded from external file or stored as multiline string
        # For now, returning a simplified version
        return open(Path(__file__).parent.parent / 'templates' / 'ui.html', 'r', encoding='utf-8').read() if (Path(__file__).parent.parent / 'templates' / 'ui.html').exists() else self._get_embedded_ui()
    
    def _get_embedded_ui(self) -> str:
        """Get embedded UI HTML (fallback)."""
        return '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Streamlet Connector</title></head>
<body><h1>Streamlet Connector Web UI</h1><p>UI is loading... If you see this, the template file is missing.</p></body>
</html>'''

    def run(self):
        """Run the Flask app."""
        print(f"\n{'='*60}")
        print(f"Streamlet Connector API Server")
        print(f"{'='*60}")
        print(f"Database: {len(self.database.get_all_items())} items loaded")
        print(f"Web UI: http://{self.host}:{self.port}/ui")
        print(f"Server: http://{self.host}:{self.port}")
        print(f"{'='*60}\n")
        print("💡 Otevřete v prohlížeči web UI:")
        print(f"   http://localhost:{self.port}/ui\n")
        
        self.app.run(host=self.host, port=self.port, debug=False, threaded=True)

    def _send_partial_file(self, file_path: str):
        """Send file with HTTP Range support for HTML5 video seeking."""
        file_size = os.path.getsize(file_path)
        range_header = request.headers.get('Range', None)
        # Robust mime detection with fallback by extension
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            ext = os.path.splitext(file_path)[1].lower()
            ext_map = {
                '.mp4': 'video/mp4',
                '.m4v': 'video/x-m4v',
                '.webm': 'video/webm',
                '.mkv': 'video/x-matroska',
                '.avi': 'video/x-msvideo',
                '.mov': 'video/quicktime',
                '.wmv': 'video/x-ms-wmv',
                '.flv': 'video/x-flv',
            }
            mime_type = ext_map.get(ext, 'application/octet-stream')

        if range_header:
            # Example Range: "bytes=0-" or "bytes=1000-2000"
            try:
                units, range_spec = range_header.split('=', 1)
                if units.strip() != 'bytes':
                    raise ValueError('Only bytes unit is supported')
                start_str, end_str = (range_spec or '').split('-', 1)
                start = int(start_str) if start_str else 0
                end = int(end_str) if end_str else file_size - 1
                # Clamp values
                start = max(0, start)
                end = min(end, file_size - 1)
                if start > end:
                    start = 0
                    end = file_size - 1

                length = end - start + 1

                def generate():
                    with open(file_path, 'rb') as f:
                        f.seek(start)
                        remaining = length
                        chunk_size = 8192
                        while remaining > 0:
                            chunk = f.read(min(chunk_size, remaining))
                            if not chunk:
                                break
                            remaining -= len(chunk)
                            yield chunk

                headers = {
                    'Content-Range': f'bytes {start}-{end}/{file_size}',
                    'Accept-Ranges': 'bytes',
                    'Content-Length': str(length),
                }
                return Response(generate(), status=206, headers=headers, mimetype=mime_type)
            except Exception:
                # Fallback to full file on parse error
                pass

        # No Range header or parse error: send full file
        headers = {
            'Accept-Ranges': 'bytes',
            'Content-Length': str(file_size),
        }
        def generate_full():
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(8192)
                    if not data:
                        break
                    yield data
        return Response(generate_full(), status=200, headers=headers, mimetype=mime_type)
