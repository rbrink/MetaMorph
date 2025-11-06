import customtkinter as ctk
from tkinter import messagebox
from PIL import Image

from core.config import Config
from core.utils import center_dialog

class ProgressDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="Progress", message="Processing..."):
        super().__init__(parent)
        self.title(title)
        self.geometry(center_dialog(parent, 500, 225))
        self.after(250, lambda: self.iconbitmap(Config.WIN_ICO['progdialog']))
        self.transient(parent)
        self.grab_set()

        self.parent = parent
        self.message = message
        self.canceled = False
        self.paused = False
        self.btn_imgs = {
            'resume': ctk.CTkImage(light_image=Image.open(Config.BTN_IMGS['resume']),
                                   dark_image=Image.open(Config.BTN_IMGS['resume']),
                                   size=(20, 20)),
            'pause': ctk.CTkImage(light_image=Image.open(Config.BTN_IMGS['pause']),
                                  dark_image=Image.open(Config.BTN_IMGS['pause']),
                                  size=(20, 20)),
            'cancel': ctk.CTkImage(light_image=Image.open(Config.BTN_IMGS['cancel']),
                                   dark_image=Image.open(Config.BTN_IMGS['cancel']),
                                   size=(20, 20)),
        }

        self._create_widgets()

    def _create_widgets(self):
        title_frame = ctk.CTkFrame(self)
        self.lbl_msg = ctk.CTkLabel(title_frame, text=self.message, wraplength=400); self.lbl_msg.pack()
        title_frame.pack(fill='x', padx=10, pady=5, anchor='center')

        progress_frame = ctk.CTkFrame(self)
        self.total_text = ctk.StringVar(value="0%")
        total_label_frame = ctk.CTkFrame(progress_frame)
        total_label_frame.grid(row=0, column=0, columnspan=3, sticky='ew')
        ctk.CTkLabel(total_label_frame, text="Total Progress:", anchor='w').pack(side='left', fill='x', expand=True, padx=10)
        ctk.CTkLabel(total_label_frame, textvariable=self.total_text, anchor='e').pack(side='right', padx=10)
        self.total_progress = ctk.CTkProgressBar(progress_frame, width=400, height=10, orientation='horizontal')
        self.total_progress.set(0.0)
        self.total_progress.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky='ew')

        self.file_text = ctk.StringVar(value="0%")
        current_label_frame = ctk.CTkFrame(progress_frame)
        current_label_frame.grid(row=2, column=0, columnspan=3, sticky='ew')
        ctk.CTkLabel(current_label_frame, text="File Progress:", anchor='w').pack(side='left', fill='x', expand=True, padx=10)
        ctk.CTkLabel(current_label_frame, textvariable=self.file_text, anchor='e').pack(side='right', padx=10)
        self.file_progress_bar = ctk.CTkProgressBar(progress_frame, width=400, height=10, orientation='horizontal')
        self.file_progress_bar.grid(row=3, column=0, columnspan=3, padx=10, pady=5, sticky='ew')
        progress_frame.pack(fill='both', pady=(10, 20), padx=30)

        btn_frame = ctk.CTkFrame(self)
        ctk.CTkButton(btn_frame, text="Cancel", image=self.btn_imgs['cancel'], compound='left', width=50,
                      command=self._on_cancel).pack(side='left', padx=2, pady=5)
        self.pause_resume = ctk.CTkButton(btn_frame, text="Pause", image=self.btn_imgs['pause'], compound='left',
                                          width=50, command=self._toggle_pause_resume)
        self.pause_resume.pack(side='left', padx=2, pady=5)
        btn_frame.pack()

    def _toggle_pause_resume(self):
        if not self.paused:
            self.master.hb.pause()
            self.pause_resume.configure(text="Resume", image=self.btn_imgs['resume'])
            self.paused = True
        else:
            self.master.hb.resume()
            self.pause_resume.configure(text="Pause", image=self.btn_imgs['pause'])
            self.paused = False

    def _on_cancel(self):
        if messagebox.askokcancel("Cancel", "Are you sure you want to cancel?"):
            self.canceled = True
            self.destroy()

    def update_progress(self, percent, message):
        # Schedule update in GUI thread
        def _update():
            self.file_progress_bar.set(percent / 100)
            self.file_text.set(f"{percent:.2f}%")
            self.lbl_msg.configure(text=message)

        self.after(0, _update)
