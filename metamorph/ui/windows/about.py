import customtkinter as ctk
from PIL import Image

from core.config import Config
from core.utils import center_dialog

class AboutWindow(ctk.CTkToplevel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.title("About")
        self.geometry(center_dialog(parent, 500, 600))
        self.iconbitmap(Config.WIN_ICO['aboutwindow'])
        self.transient(parent)
        self.grab_set()

        self.logo = ctk.CTkImage(light_image=Image.open("./metamorph/.assets/PNG/MetaMorph.png"),
                                 dark_image=Image.open("./metamorph/.assets/PNG/MetaMorph.png"),
                                 size=(128, 128))

        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self, image=self.logo).pack(padx=10, pady=10)
        ctk.CTkLabel(self, text="MetaMorph", font=("Rockwell", 16)).pack(padx=10, pady=2)
        ctk.CTkLabel(self, text=f"Version {Config.VERSION}").pack(padx=10, pady=2)
        ctk.CTkLabel(self, text="MetaMorph is a professional file transformation utility that automates renaming, metadata tagging, "
                  "and transcoding with rule-based precision.", wraplength=300,
                  justify='center').pack(padx=10, pady=5)
        ctk.CTkLabel(self, text="Tech4Fun, LLC").pack()
        ctk.CTkLabel(self, text="support@tech4fun.com", font=("Arial", 8, "underline"), text_color="#0000ff").pack()
        ctk.CTkButton(self, text="Close", width=35, command=self.destroy).pack(padx=10, pady=5)
