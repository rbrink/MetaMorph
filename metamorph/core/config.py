import os
import yaml, json
import platform
import logging
import customtkinter as ctk
from logging.handlers import RotatingFileHandler

from core.utils import resource_path

class Config:
    @staticmethod
    def asset(path: str) -> str:
        """ Return full path to an asset ICO/PNG """
        return resource_path(path)
    
    APPEARANCE_MODES = {
        'System': {'appearance_mode': 'system', 'text_color': "#000000"},
        'Light': {'appearance_mode': 'light', 'text_color': "#000000"},
        'Dark': {'appearance_mode': 'dark', 'text_color': "#ffffff"},
    }
    COLOR_THEMES = {
        'Blue': {
            'color_mode': 'blue',
            'prog_fg_color': '#3498db',
            'prog_bg_color': '#dddddd'
        },
        'Green': {
            'color_mode': 'green',
            'prog_fg_color': '#00ff00',
            'prog_bg_color': '#f0f0f0'
        },
        'Dark Blue': {
            'color_mode': 'dark-blue',
            'prog_fg_color': '#0000ff',
            'prog_bg_color': '#5a5a5a'
        },
        'Antracite':{
            'color_mode': asset("metamorph/.assets/themes/Antracite.json"),
            'prog_fg_color': "#748498",
            'prog_bg_color': "#383e3e",
        },
        'DaynNight': {
            'color_mode': asset("metamorph/.assets/themes/DaynNight.json"),
            'prog_fg_color': "#748498",
            'prog_bg_color': "#383e3e",
        },
        'Hades': {
            'color_mode': asset("metamorph/.assets/themes/Hades.json"),
            'prog_fg_color': "#fff000",
            'prog_bg_color': "#ff0000",
        },
        'Harlequin': {
            'color_mode': asset("metamorph/.assets/themes/Harlequin.json"),
            'prog_fg_color': ["#714bae", "#623c9f"],
            'prog_bg_color': ["#2a6f1e", "#1b720f"],
        },
        'NightTrain': {
            'color_mode': asset("metamorph/.assets/themes/NightTrain.json"),
            'prog_fg_color': "#00e6c3",
            'prog_bg_color': "#fff07e",
        },
        'Oceanix': {
            'color_mode': asset("metamorph/.assets/themes/Oceanix.json"),
            'prog_fg_color': ["#21375a", "#222222"],
            'prog_bg_color': ["#248e66", "#23b29a"],
        },
    }
    DEFAULTS = {
        'HB Presets JSON': r"C:/Program Files (x86)/HandBrake/presets.json" if platform.system() == "Windows" else r"/usr/bin/ghb",
        'HandBrake CLI': r"C:/Program Files (x86)/HandBrake/HandBrakeCLI.exe" if platform.system() == "Windows" else r"/usr/bin/handbrake-cli",
        'HB Preset': "Fast 1080p30",
        'Output Directory': r"./output",
        'Log Directory': r"./.logs",
        'Delete Original': False,
        'UI Appearance': 'System',
        'UI Accent': 'Blue',
    }
    BTN_IMGS = {
        'add_files': asset(".assets/PNG/plus-circle.png"),
        'add_folder': asset(".assets/PNG/folder-horizontal.png"),
        'remove_file': asset(".assets/PNG/cross-circle.png"),
        'refresh_list': asset(".assets/PNG/refresh.png"),
        'clear_list': asset(".assets/PNG/cross.png"),
        'start_batch': asset(".assets/PNG/plus.png"),
        'move_up': asset(".assets/PNG/arrow-090.png"),
        'move_down': asset(".assets/PNG/arrow-270.png"),
        'move_top': asset(".assets/PNG/arrow-top.png"),
        'move_bottom': asset(".assets/PNG/arrow-bottom.png"),
        'sort_ascend': asset(".assets/PNG/sort-ascending.png"),
        'sort_descend': asset(".assets/PNG/sort-descending.png"),
        'pause': asset(".assets/PNG/pause (32x32).png"),
        'resume': asset(".assets/PNG/start (32x32).png"),
        'cancel': asset(".assets/PNG/stop (32x32).png"),
    }
    WIN_ICO = {
        'mainwindow': asset(".assets/ICO/MetaMorph.ico"),
        'ruledialog': asset(".assets/ICO/pencil-32.ico"),
        'progdialog': asset(".assets/ICO/clock.ico"),
        'epswizard': asset(".assets/ICO/monitor.ico"),
        'settings': asset(".assets/ICO/preferences.ico"),
        'logviewer': asset(".assets/ICO/pencil-32.ico"),
        'aboutwindow': asset(".assets/ICO/question.ico"),
    }
        
    VERSION = "1.0.0"

    _config_file = "settings.conf"
    _hb_presets = None
    _data = DEFAULTS.copy()
    
    @classmethod
    def load_config(cls):
        if os.path.exists(cls._config_file):
            with open(cls._config_file, 'r') as file:
                usr_data = yaml.safe_load(file) or {}
                cls._data.update(usr_data)
    
    @classmethod
    def load_hb_presets(cls, json_path=DEFAULTS['HB Presets JSON']):
        if cls._hb_presets is None:
            with open(json_path, 'r') as file:
                data = json.load(file)
            cls._hb_presets = {}
            for category in data.get('PresetList', []):
                cat_name = category['PresetName']
                cls._hb_presets[cat_name] = {}
                for preset in category.get('ChildrenArray', []):
                    preset_name = preset.get('PresetName', "Unknown")
                    cls._hb_presets[cat_name][preset_name] = preset
        return cls._hb_presets
    
    @classmethod
    def save_config(cls):
        with open (cls._config_file, 'w') as file:
            yaml.dump(cls._data, file)
    
    @classmethod
    def get(cls, key):
        return cls._data.get(key, "")
    
    @classmethod
    def set(cls, key, value):
        cls._data[key] = value

class Logger:
    @staticmethod
    def get_logger(name, log_file="./.logs/app.log", level=logging.DEBUG):
        """
        Configure and return a logger instance
        """
        os.makedirs(Config.get("Log Directory"), exist_ok=True)
        logger = logging.getLogger(name)
        logger.setLevel(level)
        # Check if handlers are already added to avoid duplicate logs
        if not logger.handlers:
            # Create file handler with rotation
            file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
            file_handler.setLevel(level)
            # Create console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            # Define Log format
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            # Add handlers to logger
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        return logger

class ThemeManager:
    """Handles theme and accent application for CustomTkinter apps."""

    @staticmethod
    def apply(app, config_cls):
        """Apply CustomTkinter appearance and accent settings based on Config class."""

        try:
            # --- Appearance ---
            appearance_key = Config.get("UI Appearance")
            appearance_data = Config.APPEARANCE_MODES.get(
                appearance_key, Config.APPEARANCE_MODES["System"]
            )
            appearance_mode = appearance_data["appearance_mode"]
            ctk.set_appearance_mode(appearance_mode)

            # --- Accent / Color Theme ---
            accent_key = Config.get("UI Accent")
            color_data = Config.COLOR_THEMES.get(
                accent_key, Config.COLOR_THEMES["Blue"]
            )
            color_mode = color_data["color_mode"]
            ctk.set_default_color_theme(color_mode)

            # --- Optionally apply any custom widget color overrides ---
            try:
                frame_color = color_data.get("prog_bg_color")
                if frame_color:
                    app.configure(bg=frame_color)
            except Exception:
                pass

            # --- Log applied settings ---
            if hasattr(app, "logger"):
                app.logger.info(
                    f"Applied CustomTkinter theme: appearance={appearance_mode}, accent={color_mode}"
                )

        except Exception as e:
            logging.exception(f"ThemeManager failed to apply theme: {e}")
            ctk.set_appearance_mode("system")
            ctk.set_default_color_theme("blue")
