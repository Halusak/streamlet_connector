from flask import Flask, request, jsonify, send_file, render_template_string, send_from_directory
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from src.media_database import MediaDatabase
from src.scanner import MediaScanner
from src.tmdb_client import TMDBClient
from src.progress_tracker import ProgressTracker

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
        """Convert absolute local image path to URL path."""
        if not local_path:
            return None
        
        # Extract just the filename from absolute path
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
                        'poster': self._get_image_url(item.get('local_poster_path')),
                        'backdrop': self._get_image_url(item.get('local_backdrop_path')),
                        'rating': metadata.get('vote_average', 0),
                        'year': (metadata.get('release_date') or metadata.get('first_air_date', ''))[:4],
                        'overview': metadata.get('overview', '')
                    })
                else:
                    item_data['display_title'] = item_data['title']
                
                items.append(item_data)
            
            return jsonify(items), 200
        
        # ========== API: TMDB SEARCH ==========
        @self.app.route('/api/search', methods=['GET'])
        def search_tmdb():
            """Search TMDB for movies or TV shows."""
            query = request.args.get('query', '').strip()
            media_type = request.args.get('type', 'movie')  # 'movie' or 'tv'
            
            if not query:
                return jsonify({'error': 'Query parameter required'}), 400
            
            if media_type not in ['movie', 'tv']:
                return jsonify({'error': 'Type must be movie or tv'}), 400
            
            try:
                if media_type == 'movie':
                    results = self.tmdb_client.search_movies(query, limit=10)
                else:
                    results = self.tmdb_client.search_tv_shows(query, limit=10)

                # Format results
                formatted = []
                for result in results[:10]:  # Limit to 10 results
                    formatted.append({
                        'tmdb_id': result.get('id'),
                        'title': result.get('title') or result.get('name'),
                        'year': (result.get('release_date') or result.get('first_air_date', ''))[:4] if (result.get('release_date') or result.get('first_air_date')) else '',
                        'overview': result.get('overview', ''),
                        'poster_path': result.get('poster_path'),
                        'rating': result.get('vote_average', 0)
                    })

                return jsonify(formatted), 200
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
        
        # ========== API: LEGACY ENDPOINTS (kept for compatibility) ==========
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
                        'poster': item.get('local_poster_path') or metadata.get('poster_path'),
                        'rating': metadata.get('vote_average', 0)
                    })
            return jsonify(movies), 200

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
                        'poster': item.get('local_poster_path') or metadata.get('poster_path'),
                        'rating': metadata.get('vote_average', 0)
                    })
            return jsonify(tv_shows), 200

        @self.app.route('/api/movie/<int:tmdb_id>', methods=['GET'])
        def get_movie_details(tmdb_id):
            """Get complete movie details by TMDB ID."""
            for item in self.database.get_all_items():
                if item.get('type') == 'movie' and 'metadata' in item:
                    if item['metadata'].get('id') == tmdb_id:
                        result = item['metadata'].copy()
                        # Add local paths and file info
                        result['local_poster_path'] = item.get('local_poster_path')
                        result['local_backdrop_path'] = item.get('local_backdrop_path')
                        result['file_path'] = item.get('path')
                        result['year'] = item.get('year')
                        # Add internal ID for stream access
                        result['internal_id'] = self._get_item_internal_id(item)
                        return jsonify(result), 200
            return jsonify({'error': 'Movie not found'}), 404

        @self.app.route('/api/tv-show/<int:tmdb_id>', methods=['GET'])
        def get_tv_show_details(tmdb_id):
            """Get complete TV show details by TMDB ID."""
            for item in self.database.get_all_items():
                if item.get('type') == 'tv_show' and 'metadata' in item:
                    if item['metadata'].get('id') == tmdb_id:
                        result = item['metadata'].copy()
                        # Add local paths and file info
                        result['local_poster_path'] = item.get('local_poster_path')
                        result['local_backdrop_path'] = item.get('local_backdrop_path')
                        result['file_path'] = item.get('path')
                        result['seasons'] = item.get('seasons', [])
                        # Add internal ID for stream access
                        result['internal_id'] = self._get_item_internal_id(item)
                        return jsonify(result), 200
            return jsonify({'error': 'TV show not found'}), 404

        @self.app.route('/api/streams', methods=['GET'])
        def get_streams():
            """Get list of all video files (streams) with ID, name, type, size."""
            streams = []
            for idx, item in enumerate(self.database.get_all_items()):
                file_path = item.get('path')
                if file_path and os.path.exists(file_path):
                    file_stat = os.stat(file_path)
                    file_ext = os.path.splitext(file_path)[1].lower()
                    streams.append({
                        'id': idx,  # Internal ID
                        'name': os.path.basename(file_path),
                        'type': file_ext.replace('.', ''),
                        'size': file_stat.st_size,
                        'title': item.get('title', 'Unknown'),
                        'media_type': item.get('type'),
                        'tmdb_id': item.get('metadata', {}).get('id') if 'metadata' in item else None
                    })
            return jsonify(streams), 200

        @self.app.route('/api/stream/<int:stream_id>', methods=['GET'])
        def get_stream_file(stream_id):
            """Get direct link/file for stream by internal ID."""
            items = self.database.get_all_items()
            if stream_id < 0 or stream_id >= len(items):
                return jsonify({'error': 'Stream not found'}), 404
            
            item = items[stream_id]
            file_path = item.get('path')
            
            if not file_path or not os.path.exists(file_path):
                return jsonify({'error': 'File not found'}), 404
            
            try:
                # Return the actual file for streaming/download
                return send_file(
                    file_path,
                    as_attachment=False,
                    download_name=os.path.basename(file_path)
                )
            except Exception as e:
                return jsonify({'error': f'Failed to send file: {str(e)}'}), 500

        @self.app.route('/api/stream/<int:stream_id>/info', methods=['GET'])
        def get_stream_info(stream_id):
            """Get stream file information without downloading."""
            items = self.database.get_all_items()
            if stream_id < 0 or stream_id >= len(items):
                return jsonify({'error': 'Stream not found'}), 404
            
            item = items[stream_id]
            file_path = item.get('path')
            
            if not file_path or not os.path.exists(file_path):
                return jsonify({'error': 'File not found'}), 404
            
            file_stat = os.stat(file_path)
            return jsonify({
                'id': stream_id,
                'path': file_path,
                'name': os.path.basename(file_path),
                'type': os.path.splitext(file_path)[1].replace('.', ''),
                'size': file_stat.st_size,
                'url': f'/api/stream/{stream_id}'
            }), 200

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
