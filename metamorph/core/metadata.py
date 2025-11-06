import yaml
import os
import requests
import platform
import ctypes
from tkinter import messagebox
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.config import Logger

class MetadataFetcher:
    BASE_URL = "https://api.tvmaze.com"
    
    def __init__(self):
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.tvcache = Cache()
        self.logger = Logger.get_logger(__name__)
    
    def search_show(self, query):
        cache_key = f"search:{query.lower()}"
        cached = self.tvcache.get(cache_key)
        if cached:
            return cached
        url = f"{self.BASE_URL}/search/shows?q={query}"
        try:
            resp = self.session.get(url, timeout=5)
            resp.raise_for_status()
            results = resp.json()
            self.tvcache.set(cache_key, results)
            return results
        except requests.RequestException as e:
            self.logger.error(f"Failed to search show: {e}")
            messagebox.showerror("Error", f"Failed to search shows: {e}")
        return []
    
    def get_show_details(self, show_id):
        cache_key = f"show:{show_id}"
        cached = self.tvcache.get(cache_key)
        if cached:
            return cached
        url = f"{self.BASE_URL}/shows/{show_id}"
        try:
            resp = self.session.get(url, timeout=5)
            resp.raise_for_status()
            result = resp.json()
            self.tvcache.set(cache_key, result)
            return result
        except requests.RequestException as e:
            self.logger.error(f"Failed to get show detailes: {e}")
            messagebox.showerror("Error", f"Failed to get show details: {e}")
        return None
    
    def get_seasons(self, show_id):
        url = f"{self.BASE_URL}/shows/{show_id}/seasons"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        return []
    
    def get_episodes(self, show_id, season_number=None):
        cache_key = f"episodes:{show_id}"
        cached = self.tvcache.get(cache_key)
        if cached:
            filtered_cache = [ep for ep in cached if ep['season'] == season_number]
            for ep in filtered_cache:
                ep['runtime_seconds'] = (ep.get('runtime') or 42) * 60
            return filtered_cache
        url = f"{self.BASE_URL}/shows/{show_id}/episodes"
        response = self.session.get(url)
        response.raise_for_status()
        episodes = response.json()
        self.tvcache.set(cache_key, episodes)
        filtered_ep = [ep for ep in episodes if ep['season'] == season_number]
        for ep in filtered_ep:
            ep['runtime_seconds'] = (ep.get('runtime') or 42) * 60
        return filtered_ep

class Cache:
    CACHE_PATH = "./.cache"
    def __init__(self):
        if platform.system() == "Windows":
            if not os.path.exists(self.CACHE_PATH):
                try:
                    os.mkdir(self.CACHE_PATH)
                    ctypes.windll.kernel32.SetFileAttributesW(self.CACHE_PATH, 0x02)  # FILE_ATTRIBUTE_HIDDEN
                except OSError as e:
                    messagebox.showwarning("Warning", f"Failed to create hidden cache directory: {e}")
        else:
            # Ensure the path starts with a dot for conventional hiding
            if not os.path.basename(self.CACHE_PATH).startswith('.'):
                # Prepend a dot to the last component of the path
                dir_name = os.path.basename(self.CACHE_PATH)
                parent_dir = os.path.dirname(self.CACHE_PATH)
                path = os.path.join(parent_dir, f".{dir_name}")
            
            try:
                os.makedirs(path, exist_ok=True)
            except OSError as e:
                messagebox.showerror("Error", f"Error creating directory on Unix-like system: {e}")
        self._cache_file = os.path.join(self.CACHE_PATH, "tvmaze_cache.yaml")
        self.cache = self.load_cache()

    def load_cache(self):
        if os.path.exists(self._cache_file):
            with open(self._cache_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def save_to_cache(self):
        with open(self._cache_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.cache, f, allow_unicode=True)
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, value):
        self.cache[key] = value
        self.save_to_cache()
