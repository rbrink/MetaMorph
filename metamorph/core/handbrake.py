import os
import sys
import re
import psutil
import subprocess
from tkinter import messagebox

from core.config import Config, Logger

class HandBrake:
    def __init__(self):
        self.logger = Logger.get_logger(__name__)
        self.process = None

    def _extract_percent(self, line):
        match = re.search(r'(\d{1,3}\.\d{1,2})\s?%', line)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None

    def _parse_filename(self, filename):
        """
        Parse filename for show name (with year) and season number.
        Example: "My Show Name (1990) S02E05.mkv"
        Returns (show_title_with_year, season_folder)
        """
        match = re.search(r"^(.*?\(\d{4}\))\s*S(\d{2})E\d{2}", filename, re.IGNORECASE)
        if match:
            title_with_year, season = match.groups()
            sn_folder = f"Season {season}"    # Preserves leading zero
            return title_with_year.strip(), sn_folder
        return None, None
    
    def pause(self):
        if self.process and self.process.poll() is None:
            psutil.Process(self.process.pid).suspend()
            self.logger.info("HandBrake process paused.")

    def resume(self):
        if self.process and self.process.poll() is None:
            psutil.Process(self.process.pid).resume()
            self.logger.info("HandBrake process resumed.")
    
    def transcode(self, input_file, output_dir, progress_callback=None,
                  done_callback=None, del_original=False, cancel_flag=None):
        """
        Run HandBrakeCLI on a file, updating progress via callback.
        """
        os.makedirs(output_dir, exist_ok=True)
        # Ensure output file has a safe extension (e.g., mkv)
        base_name, _ = os.path.splitext(os.path.basename(input_file))
        # Determine target directory structure
        show_title, season_dir = self._parse_filename(base_name)
        if show_title and season_dir:
            final_dir = os.path.join(output_dir, show_title, season_dir)
        else:    # Fallback: dump to output_dir directly
            final_dir = output_dir
        os.makedirs(final_dir, exist_ok=True)
        output_file = os.path.join(final_dir, base_name + ".mkv")

        # For Windows only: prevent console popups
        CREATE_NO_WINDOW = 0x08000000

        cmd = [
            Config.get('HandBrake CLI'), 
            "--preset-import-file", Config.get('HB Presets JSON'),
            "-Z", Config.get('HB Preset'),
            "-i", input_file,
            "-o", output_file
        ]
        self.logger.info(f"Running command: {cmd}")
        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                                            creationflags=CREATE_NO_WINDOW if sys.platform == "win32" else 0, errors="replace", bufsize=1)
            for line in self.process.stdout:
                if cancel_flag and cancel_flag():
                    self.process.terminate()
                    if done_callback:
                        done_callback(success=False, input_file=input_file, output_file=None, cancelled=True)
                    return
                
                percent = self._extract_percent(line)
                if percent is not None and progress_callback:
                    base = os.path.basename(input_file)
                    progress_callback(percent, base)
            self.process.wait()

            if self.process.returncode == 0:
                if done_callback:
                    done_callback(success=True, input_file=input_file, output_file=output_file)

                if del_original:
                    try:
                        os.remove(input_file)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to delete original file: {e}")
                        self.logger.error(f"Failed to delete original file: {e}")
            else:
                if done_callback:
                    done_callback(success=False, input_file=input_file, output_file=None)
        except FileNotFoundError:
            messagebox.showerror("Error", "HandBrakeCLI not found. Please check the installation path in Config.")
            self.logger.error("HandBrakeCLI not found. Please check the installation path in Config.")
            if done_callback:
                done_callback(success=False, input_file=input_file, output_file=None)
