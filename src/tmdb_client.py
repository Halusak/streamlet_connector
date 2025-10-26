import os
import requests
from tmdbv3api import TMDb, Movie, TV
from typing import Optional, Dict, List

class TMDBClient:
    """Client for TMDB API to fetch media metadata."""

    def __init__(self, api_key: str, language: str = 'en-US'):
        # Store raw values for fallback HTTP calls
        self.api_key = api_key
        self.language = language
        if api_key:
            self.tmdb = TMDb()
            self.tmdb.api_key = api_key
            self.tmdb.language = language
            self.movie_api = Movie()
            self.tv_api = TV()
        else:
            self.tmdb = None
            self.movie_api = None
            self.tv_api = None

    def search_movie(self, title: str, year: Optional[int] = None) -> Optional[Dict]:
        """Search for movie and return metadata."""
        if not self.movie_api:
            return None

        try:
            results = self.movie_api.search(title)
            if results:
                movie = results[0]  # Take first result
                if year and hasattr(movie, 'release_date') and movie.release_date:
                    try:
                        movie_year = movie.release_date.year
                        if abs(movie_year - year) > 1:
                            return None  # Year mismatch
                    except:
                        pass
                details = self.movie_api.details(movie.id)
                return {
                    'id': movie.id,
                    'title': movie.title,
                    'original_title': movie.original_title,
                    'release_date': str(movie.release_date) if movie.release_date else None,
                    'overview': movie.overview,
                    'poster_path': movie.poster_path,
                    'backdrop_path': movie.backdrop_path,
                    'genres': [g.name for g in details.genres] if hasattr(details, 'genres') else [],
                    'runtime': details.runtime if hasattr(details, 'runtime') else None,
                    'vote_average': movie.vote_average
                }
        except Exception as e:
            print(f"Error searching movie {title}: {e}")
        return None

    def search_tv_show(self, title: str) -> Optional[Dict]:
        """Search for TV show and return metadata."""
        if not self.tv_api:
            return None

        try:
            results = self.tv_api.search(title)
            if results:
                show = results[0]  # Take first result
                details = self.tv_api.details(show.id)
                return {
                    'id': show.id,
                    'name': show.name,
                    'original_name': show.original_name,
                    'first_air_date': str(show.first_air_date) if show.first_air_date else None,
                    'overview': show.overview,
                    'poster_path': show.poster_path,
                    'backdrop_path': show.backdrop_path,
                    'genres': [g.name for g in details.genres] if hasattr(details, 'genres') else [],
                    'number_of_seasons': details.number_of_seasons if hasattr(details, 'number_of_seasons') else None,
                    'number_of_episodes': details.number_of_episodes if hasattr(details, 'number_of_episodes') else None,
                    'vote_average': show.vote_average
                }
        except Exception as e:
            print(f"Error searching TV show {title}: {e}")
        return None

    def get_movie_details(self, tmdb_id: int) -> Optional[Dict]:
        """Get full movie details by TMDB ID."""
        if not self.movie_api:
            return None

        try:
            details = self.movie_api.details(tmdb_id)
            if not details:
                return None
            # Some attributes may be missing depending on API/version
            return {
                'id': details.id,
                'title': getattr(details, 'title', None),
                'original_title': getattr(details, 'original_title', None),
                'overview': getattr(details, 'overview', ''),
                'tagline': getattr(details, 'tagline', ''),
                'poster_path': getattr(details, 'poster_path', None),
                'backdrop_path': getattr(details, 'backdrop_path', None),
                'release_date': str(getattr(details, 'release_date', '') or '') or None,
                'runtime': getattr(details, 'runtime', None),
                'vote_average': getattr(details, 'vote_average', 0),
                'vote_count': getattr(details, 'vote_count', 0),
                'genres': [g.name for g in getattr(details, 'genres', [])] if getattr(details, 'genres', None) else [],
                'original_language': getattr(details, 'original_language', ''),
                'production_countries': [c.name for c in getattr(details, 'production_countries', [])] if getattr(details, 'production_countries', None) else [],
                'production_companies': [c.name for c in getattr(details, 'production_companies', [])] if getattr(details, 'production_companies', None) else [],
                'spoken_languages': [l.english_name for l in getattr(details, 'spoken_languages', [])] if getattr(details, 'spoken_languages', None) else [],
                'status': getattr(details, 'status', ''),
                'budget': getattr(details, 'budget', 0),
                'revenue': getattr(details, 'revenue', 0),
                'homepage': getattr(details, 'homepage', ''),
                'imdb_id': getattr(details, 'imdb_id', None),
                'adult': getattr(details, 'adult', False),
                'video': getattr(details, 'video', False),
                'popularity': getattr(details, 'popularity', 0),
                'origin_country': getattr(details, 'origin_country', [])
            }
        except Exception as e:
            print(f"Error getting movie details {tmdb_id}: {e}")
            return None

    def get_tv_show_details(self, tmdb_id: int) -> Optional[Dict]:
        """Get full TV show details by TMDB ID."""
        if not self.tv_api:
            return None

        try:
            details = self.tv_api.details(tmdb_id)
            if not details:
                return None
            return {
                'id': details.id,
                'name': getattr(details, 'name', None),
                'original_name': getattr(details, 'original_name', None),
                'overview': getattr(details, 'overview', ''),
                'tagline': getattr(details, 'tagline', ''),
                'poster_path': getattr(details, 'poster_path', None),
                'backdrop_path': getattr(details, 'backdrop_path', None),
                'first_air_date': str(getattr(details, 'first_air_date', '') or '') or None,
                'last_air_date': str(getattr(details, 'last_air_date', '') or '') or None,
                'vote_average': getattr(details, 'vote_average', 0),
                'vote_count': getattr(details, 'vote_count', 0),
                'genres': [g.name for g in getattr(details, 'genres', [])] if getattr(details, 'genres', None) else [],
                'original_language': getattr(details, 'original_language', ''),
                'production_countries': [c.name for c in getattr(details, 'production_countries', [])] if getattr(details, 'production_countries', None) else [],
                'production_companies': [c.name for c in getattr(details, 'production_companies', [])] if getattr(details, 'production_companies', None) else [],
                'spoken_languages': [l.english_name for l in getattr(details, 'spoken_languages', [])] if getattr(details, 'spoken_languages', None) else [],
                'status': getattr(details, 'status', ''),
                'homepage': getattr(details, 'homepage', ''),
                'adult': getattr(details, 'adult', False),
                'popularity': getattr(details, 'popularity', 0),
                'origin_country': getattr(details, 'origin_country', []),
                'number_of_episodes': getattr(details, 'number_of_episodes', None),
                'number_of_seasons': getattr(details, 'number_of_seasons', None),
                'episode_run_time': getattr(details, 'episode_run_time', []),
                'languages': getattr(details, 'languages', []),
                'networks': [n.name for n in getattr(details, 'networks', [])] if getattr(details, 'networks', None) else [],
                'created_by': [c.name for c in getattr(details, 'created_by', [])] if getattr(details, 'created_by', None) else [],
                'last_episode_to_air': getattr(details, 'last_episode_to_air', {}).get('air_date') if getattr(details, 'last_episode_to_air', None) else None,
                'next_episode_to_air': getattr(details, 'next_episode_to_air', {}).get('air_date') if getattr(details, 'next_episode_to_air', None) else None
            }
        except Exception as e:
            print(f"Error getting TV show details {tmdb_id}: {e}")
            return None

    def search_movies(self, title: str, limit: int = 5) -> List[Dict]:
        """Search for movies and return multiple results."""
        if not self.movie_api:
            return []

        try:
            results = self.movie_api.search(title)
            movies = []
            for movie in results[:limit]:
                try:
                    details = self.movie_api.details(movie.id)
                    movies.append({
                        'id': movie.id,
                        'title': movie.title,
                        'original_title': movie.original_title,
                        'release_date': str(movie.release_date) if movie.release_date else None,
                        'overview': movie.overview,
                        'poster_path': movie.poster_path,
                        'backdrop_path': movie.backdrop_path,
                        'genres': [g.name for g in details.genres] if hasattr(details, 'genres') else [],
                        'runtime': details.runtime if hasattr(details, 'runtime') else None,
                        'vote_average': movie.vote_average
                    })
                except:
                    continue
            return movies
        except Exception as e:
            print(f"Error searching movies {title}: {e}")
        return []

    def search_tv_shows(self, title: str, limit: int = 5) -> List[Dict]:
        """Search for TV shows and return multiple results."""
        if not self.tv_api:
            return []

        try:
            results = self.tv_api.search(title)
            shows = []
            for show in results[:limit]:
                try:
                    details = self.tv_api.details(show.id)
                    shows.append({
                        'id': show.id,
                        'name': show.name,
                        'original_name': show.original_name,
                        'first_air_date': str(show.first_air_date) if show.first_air_date else None,
                        'overview': show.overview,
                        'poster_path': show.poster_path,
                        'backdrop_path': show.backdrop_path,
                        'genres': [g.name for g in details.genres] if hasattr(details, 'genres') else [],
                        'number_of_seasons': details.number_of_seasons if hasattr(details, 'number_of_seasons') else None,
                        'number_of_episodes': details.number_of_episodes if hasattr(details, 'number_of_episodes') else None,
                        'vote_average': show.vote_average
                    })
                except:
                    continue
            return shows
        except Exception as e:
            print(f"Error searching TV shows {title}: {e}")
        return []

    def get_tv_episode_details(self, tmdb_id: int, season_number: int, episode_number: int) -> Optional[Dict]:
        """Get TV episode details by show TMDB ID, season and episode number using HTTP fallback."""
        if not self.api_key:
            return None
        try:
            url = (
                f"https://api.themoviedb.org/3/tv/{tmdb_id}"
                f"/season/{season_number}/episode/{episode_number}"
            )
            params = {"api_key": self.api_key, "language": self.language or "en-US"}
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            # Normalize subset of fields
            return {
                'id': data.get('id'),
                'name': data.get('name'),
                'overview': data.get('overview', ''),
                'air_date': data.get('air_date'),
                'season_number': data.get('season_number', season_number),
                'episode_number': data.get('episode_number', episode_number),
                'episode_type': data.get('episode_type'),
                'still_path': data.get('still_path'),
                'vote_average': data.get('vote_average', 0),
                'vote_count': data.get('vote_count', 0),
                'runtime': data.get('runtime'),
                'show_id': tmdb_id
            }
        except Exception as e:
            print(f"Error getting TV episode details for {tmdb_id} S{season_number}E{episode_number}: {e}")
            return None

    def get_tv_season_episodes(self, tmdb_id: int, season_number: int) -> List[Dict]:
        """Get all episodes for a TV season with normalized fields."""
        if not self.api_key:
            return []
        try:
            url = f"https://api.themoviedb.org/3/tv/{tmdb_id}/season/{season_number}"
            params = {"api_key": self.api_key, "language": self.language or "en-US"}
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json() or {}
            episodes = data.get('episodes', []) or []
            normalized = []
            for ep in episodes:
                normalized.append({
                    'id': ep.get('id'),
                    'name': ep.get('name'),
                    'overview': ep.get('overview', ''),
                    'air_date': ep.get('air_date'),
                    'episode_number': ep.get('episode_number'),
                    'episode_type': ep.get('episode_type'),
                    'runtime': ep.get('runtime'),
                    'season_number': ep.get('season_number', season_number),
                    'show_id': tmdb_id,
                    'still_path': ep.get('still_path'),
                    'vote_average': ep.get('vote_average', 0)
                })
            return normalized
        except Exception as e:
            print(f"Error getting TV season episodes for {tmdb_id} S{season_number}: {e}")
            return []