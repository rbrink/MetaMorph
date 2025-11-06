import threading, time
import customtkinter as ctk
from PIL import Image

from core.config import Config, ThemeManager
from core.utils import  center_toscreen, safe_after, bring_to_front
from ui.windows.main_window import Application

ctk.set_appearance_mode(
            Config.APPEARANCE_MODES[Config.get('UI Appearance')]['appearance_mode']
)
ctk.set_default_color_theme(
            Config.COLOR_THEMES[Config.get('UI Accent')]['color_mode']
)

class SplashScreen:
    def __init__(self, root):
        self.root = root
        self.root.geometry(center_toscreen(self.root, 500, 500))
        self.root.overrideredirect(True)
        self.root.resizable(False, False)

        logo = ctk.CTkImage(light_image=Image.open(Config.asset(".assets/PNG/MetaMorph.png")),
                            dark_image=Image.open(Config.asset(".assets/PNG/MetaMorph.png")),
                            size=(256, 256))
        ctk.CTkLabel(self.root, text="", image=logo).pack(pady=20)
        ctk.CTkLabel(self.root, text="MetaMorph", font=("Rockwell", 24)).pack(pady=20)
        
        ctk.CTkLabel(self.root, text="Please wait...", font=("Arial", 12)).pack(pady=(20, 0))
        self.loading_app = ctk.CTkProgressBar(self.root, width=200, height=15, orientation='horizontal', mode="indeterminate")
        self.loading_app.pack(pady=(5, 20))

        bring_to_front(self.root)
        self.thread = threading.Thread(target=self.loading, daemon=True).start()
        self.loading_app.start()

    def loading(self):
        print("DEBUG: Entered Thread")
        time.sleep(3)
        self.loading_app.stop()
        safe_after(self.root, 250, self.close_splash_open_main)
    
    def close_splash_open_main(self):
        print("DEBUG: Closing Splash and Opening Main App")
        if self.root.winfo_exists():
            self.root.destroy()
            Config.load_config()
            app = Application()
            ThemeManager.apply(app, Config)
            bring_to_front(app)
            app.mainloop()

if __name__ == "__main__":
    root = ctk.CTk()
    SplashScreen(root)
    root.mainloop()