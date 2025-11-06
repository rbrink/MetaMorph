import customtkinter as ctk
from typing import Optional

from core.utils import center_dialog
from ui.widgets import CTkLabelInput

class OverrideDialog(ctk.CTkToplevel):
    def __init__(self, master: ctk.CTkBaseClass, title: str = None, prompt: str = None, initialvalue: str = "", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        # ----- Window Setup -----
        self.title(title if title else "Override Filename")
        self.geometry(center_dialog(master, 500, 150))
        self.resizable(False, False)
        self.grab_set()    # Make dialog modal
        self.transient(master)    # Set to be on top of master
        self.focus_force()    # Focus on this window
        # ----- Attributes -----
        self.master = master
        self.prompt = prompt if prompt else "Enter new filename:"
        self.initialvalue = initialvalue
        self.result: Optional[str] = None

        self.create_widgets()

    def create_widgets(self):
        # ----- Prompt and Entry -----
        self.entry_var = ctk.StringVar(value=self.initialvalue)
        self.entry = CTkLabelInput(self, label= self.prompt, input_class=ctk.CTkEntry, input_var=self.entry_var,
                                   label_args={'anchor': 'w'}, input_args={'width': 400}, stacked=True)
        self.entry.pack(pady=(20, 10))
        self.entry.input.focus()
        self.entry.input.select_range(0, ctk.END)
        self.entry.input.bind("<Return>", lambda event: self.on_ok())
        # ----- Button Frame -----
        btn_frame = ctk.CTkFrame(self)
        btn_ok = ctk.CTkButton(btn_frame, text="OK", width=80, command=self.on_ok)
        btn_ok.pack(side=ctk.LEFT, padx=(0, 10))
        btn_cancel = ctk.CTkButton(btn_frame, text="Cancel", width=80, command=self.on_cancel)
        btn_cancel.pack(side=ctk.LEFT)
        btn_frame.pack(pady=(0, 20))

    def on_ok(self):
        self.result = self.entry_var.get().strip()
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()
