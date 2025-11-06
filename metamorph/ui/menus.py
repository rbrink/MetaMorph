import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk

from core.config import Config

class MainMenu(tk.Menu):
    def __init__(self, master, callbacks, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.callbacks = callbacks

        self.create_menus()

    def create_menus(self):
        # ----- File Menu -----
        file_menu = tk.Menu(self, tearoff=0)
        file_menu.add_command(label="Add Files", command=self.callbacks.get('add_files'))
        file_menu.add_command(label="Add Folder", command=self.callbacks.get('add_folder'))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)
        self.add_cascade(label="File", menu=file_menu)
        # ----- Edit Menu -----
        edit_menu = tk.Menu(self, tearoff=0)
        edit_menu.add_command(label="Refresh List", command=self.callbacks.get('refresh_list'))
        edit_menu.add_command(label="Clear List", command=self.callbacks.get('clear_list'))
        edit_menu.add_separator()
        edit_menu.add_command(label="Settings", command=self.callbacks.get('settings'))
        self.add_cascade(label="Edit", menu=edit_menu)
        # ----- Import Menu -----
        import_menu = tk.Menu(self, tearoff=0)
        import_menu.add_command(label="Import TV Show", command=self.callbacks['import_tv'], underline=1)
        import_menu.add_command(label="Import Data from CSV", command=self.callbacks['import_csv_data'])
        self.add_cascade(label="Import", menu=import_menu, underline=0)
        # ----- Help Menu -----
        help_menu = tk.Menu(self, tearoff=0)
        help_menu.add_command(label="About", command=self.callbacks.get('about'))
        self.add_cascade(label="Help", menu=help_menu)

class ToolBar(ctk.CTkFrame):
    def __init__(self, master, callbacks: dict, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        # ----- Attributes -----
        self.master = master
        self.callbacks = callbacks
        self.btn_imgs = {
            'add_files': ctk.CTkImage(light_image=Image.open(Config.BTN_IMGS['add_files']),
                                      dark_image=Image.open(Config.BTN_IMGS['add_files']),
                                      size=(32, 32)),
            'add_folder': ctk.CTkImage(light_image=Image.open(Config.BTN_IMGS['add_folder']),
                                       dark_image=Image.open(Config.BTN_IMGS['add_folder']),
                                       size=(32, 32)),
            'refresh_list': ctk.CTkImage(light_image=Image.open(Config.BTN_IMGS['refresh_list']),
                                         dark_image=Image.open(Config.BTN_IMGS['refresh_list']),
                                         size=(32, 32)),
            'clear_list': ctk.CTkImage(light_image=Image.open(Config.BTN_IMGS['clear_list']),
                                       dark_image=Image.open(Config.BTN_IMGS['clear_list']),
                                       size=(32, 32)),
        }

        self.create_widgets()

    def create_widgets(self):
        btn_addfiles = ctk.CTkButton(self, text="Add Files", image=self.btn_imgs['add_files'],
                                     compound='left', command=self.callbacks.get('add_files'))
        btn_addfiles.pack(side='left', padx=5, pady=5)
        btn_addfolder = ctk.CTkButton(self, text="Add Folder", image=self.btn_imgs['add_folder'],
                                      compound='left', command=self.callbacks.get('add_folder'))
        btn_addfolder.pack(side='left', padx=5, pady=5)
        btn_refresh = ctk.CTkButton(self, text="Refresh", image=self.btn_imgs['refresh_list'],
                                    compound='left', command=self.callbacks.get('refresh_list'))
        btn_refresh.pack(side='left', padx=5, pady=5)
        btn_clearlist = ctk.CTkButton(self, text="Clear List", image=self.btn_imgs['clear_list'],
                                      compound='left', command=self.callbacks.get('clear_list'))
        btn_clearlist.pack(side='left', padx=5, pady=5)

class FileContextMenu(tk.Menu):
    def __init__(self, master, callbacks, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.callbacks = callbacks
        self.context_imgs = {
            'add': ImageTk.PhotoImage(Image.open(Config.BTN_IMGS['add_files']).resize((16, 16))),
            'remove': ImageTk.PhotoImage(Image.open(Config.BTN_IMGS['remove_file']).resize((16, 16))),
            'refresh': ImageTk.PhotoImage(Image.open(Config.BTN_IMGS['refresh_list']).resize((16, 16))),
        }

        self.create_menu()

    def create_menu(self):
        mv_selected_menu = tk.Menu(self, tearoff=0)
        mv_selected_menu.add_command(label="Move Top", command=self.callbacks['move_top'])
        mv_selected_menu.add_command(label="Move Up", command=self.callbacks['move_up'])
        mv_selected_menu.add_command(label="Move Down", command=self.callbacks['move_down'])
        mv_selected_menu.add_command(label="Move Bottom", command=self.callbacks['move_bottom'])
        self.add_cascade(label="Move Selected", menu=mv_selected_menu)

        sort_menu = tk.Menu(self)
        sort_menu.add_command(label="Sort Ascending", command=self.callbacks['sort_ascend'])
        sort_menu.add_command(label="Sort Descending", command=self.callbacks['sort_descend'])
        self.add_cascade(label="Sort", menu=sort_menu)
        self.add_separator()

        self.add_command(label="Add", image=self.context_imgs['add'], compound=tk.LEFT, command=self.callbacks['add_files'])
        self.add_command(label="Remove", image=self.context_imgs['remove'], compound=tk.LEFT, command=self.callbacks['remove_file'])
        self.add_separator()

        self.add_command(label="Run", command=lambda: messagebox.showinfo("TBI", "To Be Implemented"))
        self.add_command(label="Open containing folder", command=lambda: messagebox.showinfo("TBI", "To Be Implemented"))
        self.add_command(label="Properties", command=lambda: messagebox.showinfo("TBI", "To Be Implemented"))
        self.add_command(label="Override filename", command=self.callbacks['override_name'])
        self.add_separator()

        self.add_command(label="Refresh", image=self.context_imgs['refresh'], compound=tk.LEFT, command=self.callbacks['refresh_list'])
