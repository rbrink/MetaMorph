import sys
import platform
from pathlib import Path
from ctypes import windll

def bring_to_front(window):
    """Force a CTk or Tk window to the foreground on Windows."""
    try:
        window.lift()
        window.attributes('-topmost', True)
        window.after(200, lambda: window.attributes('-topmost', False))
        window.focus_force()
        # ----- Windows -----
        if platform.system() == "Windows":
            try:
                hwnd = windll.user32.GetParent(window.winfo_id())
                windll.user32.ShowWindow(hwnd, 5)       # SW_SHOW
                windll.user32.BringWindowToTop(hwnd)
                windll.user32.SetActiveWindow(hwnd)
                windll.user32.SetForegroundWindow(hwnd)
            except Exception as e:
                print(f"[bring_to_front] Windows focus handling failed: {e}")
        # ----- macOS -----
        elif platform.system() == "Darwin":
            try:
                # Tk usually obeys lift(), but sometimes needs this
                window.lift()
                window.focus_force()
            except Exception as e:
                print(f"[bring_to_front] macOS handling failed: {e}")
        # --- Linux / X11 fallback ---
        elif platform.system() == "Linux":
            try:
                window.lift()
                window.attributes("-topmost", True)
                window.after(200, lambda: window.attributes("-topmost", False))
            except Exception as e:
                print(f"[bring_to_front] Linux handling failed: {e}")
    except Exception as e:
        print("DEBUG: bring_to_front failed:", e)

def center_toscreen(window, width, height):
    """ Center Window to Display """
    # Ensure the window's dimensions are calculated by the geometry manager
    window.update_idletasks()

    # Get window dimensions
    window_width = width
    window_height = height

    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate x and y coordinates for centering
    x_coordinate = (screen_width - window_width) // 2
    y_coordinate = (screen_height - window_height) // 2

    # Set the window's geometry
    return f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}"

def center_dialog(master, width, height):
    master.update_idletasks()
    root_x, root_y = master.winfo_x(), master.winfo_y()
    root_w, root_h = master.winfo_width(), master.winfo_height()
    x = root_x + (root_w - width) // 2
    y = root_y + (root_h - height) // 2
    return f"{width}x{height}+{x}+{y}"

def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and PyInstaller."""
    try:
        # When running as a bundle, PyInstaller stores files in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # When running normally
        base_path = Path(__file__).resolve().parent.parent  # goes up to /metamorph
    return str(base_path / relative_path)

def safe_after(widget, delay, func=None, *args, **kwargs):
    """Wraps .after() calls to log what function is being scheduled."""
    import traceback
    def wrapped():
        try:
            if callable(func):
                func(*args, **kwargs)
            else:
                print(f"[ERROR] Scheduled non-callable func: {repr(func)}")
        except Exception as e:
            print(f"\n=== AFTER CALLBACK ERROR ===\n{e}")
            traceback.print_exc()
    return widget.after(delay, wrapped)