import threading
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

from core.config import Config, Logger
from core.utils import center_dialog
from core.metadata import MetadataFetcher
from ui.widgets import CTkLabelInput, CTkLabelFrame

class EpisodeMetadata(ctk.CTkToplevel):
    def __init__(self, master: ctk.CTkBaseClass, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title("Import TV Show Metadata")
        self.after(250, lambda: self.iconbitmap(Config.WIN_ICO['epswizard']))
        self.geometry(center_dialog(master, 650, 450))
        #self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.focus_force()
        # ----- Attributes -----
        self.show_results = []
        self.episodes = []
        self.selected_show = None
        self.selected_episodes = []
        self.logger = Logger.get_logger(__name__)

        self.create_widgets()
        self.show_page_1()

        self.wait_window()

    def create_widgets(self):
        # ----- Top Spacer -----
        frm_spcr = ctk.CTkFrame(self, height=40)
        frm_spcr.pack(fill='x')
        # ----- Page 1: Search and Select Show -----
        self.page1 = ctk.CTkFrame(self)
        frm_searchshow = ctk.CTkFrame(self.page1)
        self.query = CTkLabelInput(frm_searchshow, label="Search TV Show:", input_class=ctk.CTkEntry, input_args={'width': 250})
        self.query.grid(row=0, column=0, padx=5)
        self.query.input.bind("<Return>", self._search_shows)
        self.after(100, lambda: self.query.input.focus_set())
        ctk.CTkButton(frm_searchshow, text="Search", command=self._search_shows).grid(row=0, column=1, padx=5)
        frm_searchshow.pack(fill='x', padx=60, pady=5)
        self.show_list = tk.Listbox(self.page1, width=100, height=15, font=("Helvetica", 12))
        self.show_list.bind("<<ListboxSelect>>", self._on_show_select)
        self.show_list.pack(padx=100, pady=10)

        self.lbl_selected_show = ctk.CTkLabel(self.page1, text="Selected Show:")
        self.lbl_selected_show.pack(padx=80, anchor='w')
        self.lbl_selected_showgenre = ctk.CTkLabel(self.page1, text="Genre:")
        self.lbl_selected_showgenre.pack(padx=80, anchor='w')

        pg1btn_frame = ctk.CTkFrame(self.page1)
        ctk.CTkButton(pg1btn_frame, text="Cancel", width=35, command=self.destroy).pack(side='left', padx=5)
        ctk.CTkButton(pg1btn_frame, text="Next >", width=35, command=self.show_page_2).pack(side='left', padx=5)
        pg1btn_frame.pack(side='bottom', padx=15, pady=10, anchor='e')
        # ----- Page 2: Episode Selection -----
        self.page2 = ctk.CTkFrame(self)
        content = ctk.CTkFrame(self.page2)
        content.pack(fill='both', padx=5, pady=5)
        # Season List
        self.side1 = CTkLabelFrame(content, label="  Season(s):", font=ctk.CTkFont(size=10, weight='bold'), label_bg="#95a5a6")
        self.season_frame = ctk.CTkScrollableFrame(self.side1, fg_color="transparent")
        self.season_frame.pack(fill='both')
        self.side1.pack(side='left', fill='y', padx=(10, 5), pady=5)
        # Episode List
        self.side2 = CTkLabelFrame(content, label="  Episodes:", font=ctk.CTkFont(size=10, weight='bold'), label_bg="#95a5a6")
        self.episode_frame = ctk.CTkScrollableFrame(self.side2, fg_color="transparent")
        self.episode_frame.pack(fill='both')
        self.side2.pack(side='left', fill='both', expand=True, padx=(10, 5), pady=5)

        frame = ctk.CTkFrame(self.page2)
        self.toggle = ctk.CTkButton(frame, text="Select All", width=35, command=self._toggle_select)
        self.toggle.pack(side='left', padx=20, pady=5)
        self.lbl_len_episodelist = ctk.CTkLabel(frame, text="Selected episode count:", width=50, font=ctk.CTkFont(size=10))
        self.lbl_len_episodelist.pack(side='left', padx=80, pady=5)
        self.lbl_len_filelist = ctk.CTkLabel(frame, text="File list count:", width=50, font=ctk.CTkFont(size=10))
        self.lbl_len_filelist.pack(side='left', padx=100, pady=5, anchor='w')        
        frame.pack(fill='x', padx=5)

        pg2btn_frame = ctk.CTkFrame(self.page2)
        ctk.CTkButton(pg2btn_frame, text="Cancel", width=35, command=self.destroy).pack(side='right', padx=5)
        ctk.CTkButton(pg2btn_frame, text="OK", width=35, command=self.on_ok).pack(side='right', padx=5)
        ctk.CTkButton(pg2btn_frame, text="< Previous", width=35, command=self.show_page_1).pack(side='right', padx=5)
        pg2btn_frame.pack(side='bottom', fill='x', padx=15, pady=10)
    
    def show_page_1(self):
        # ----- Clear season/episode lists -----
        for w in self.episode_frame.winfo_children():
            w.destroy()
        self.season_episode_vars = {}

        self.toggle.configure(text="Select All", command=self._toggle_select)
        self.page2.pack_forget()
        self.page1.pack(fill='both', expand=True)

    def show_page_2(self):
        # ----- Clear any existing checkboxes -----
        for w in self.season_frame.winfo_children():
            w.destroy()
        self.season_vars = []
        selected = self.show_list.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a TV show first.")
            return
        self.selected_show = self.show_results[selected[0]]['show']
        self.seasons = MetadataFetcher().get_seasons(self.selected_show['id'])
        self.lbl_selected_show.configure(text=f"Selected Show: {self.selected_show['name']}")

        for season in self.seasons:
            var = tk.BooleanVar(value=False) # Default is unchecked
            chkbx = ctk.CTkCheckBox(self.season_frame, text=f"Season {season['number']}", variable=var)
            chkbx.configure(command=self._on_season_select)
            chkbx.pack(anchor=tk.W, padx=5, pady=2)
            self.season_vars.append((var, season))    # Store the BooleanVar and season info
        self.lbl_len_filelist.configure(text=f"File list count: {len(self.master.file_list.get_children())}")
        self.page1.pack_forget()
        self.page2.pack(fill='both', expand=True)
    
    def on_ok(self):
        selected = []
        for var, ep in self.episode_vars:
            if var.get():
                self.selected_episodes.append(ep)
        self.destroy()

    def _search_shows(self, event=None):
        query = self.query.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query.")
            return
        self.show_results = MetadataFetcher().search_show(query)
        self.show_list.delete(0, tk.END)
        for item in self.show_results:
            show = item['show']
            name = show.get('name', 'Unknown')
            year = show.get('premiered', 'N/A')[:4] if show.get('premiered') else 'N/A'
            self.show_list.insert(tk.END, f"{name} ({year})")
    
    def _on_show_select(self, event):
        selected = self.show_list.curselection()
        if selected:
            show = self.show_results[selected[0]]['show']
            self.lbl_selected_show.configure(text=f"Selected Show: {show['name']} ({show['premiered'][:4]})")
            self.lbl_selected_showgenre.configure(text=f"Genre: {show['genres']}")
        else:
            self.lbl_selected_show.configure(text="Selected Show: ")
            self.lbl_selected_showgenre.configure(text="Genre: ")

    def _on_season_select(self):
        # Get selected seasons from the checkboxes
        selected = [season for var, season in self.season_vars if var.get()]
        if not selected:
            for w in self.episode_frame.winfo_children():
                w.destroy()
            self.lbl_len_episodelist.configure(text="Selected episode count: 0", 
                                               text_color="#ffffff")
            self.toggle.configure(text="Select All", command=self._toggle_select)
            return
        
        def load_episodes(selected):
            all_episodes = []
            show_id = self.selected_show['id']
            # Fetch episodes for the selected seasons
            for season in selected:
                try:
                    eps = MetadataFetcher().get_episodes(show_id, season['number'])
                    all_episodes.extend(eps)
                except Exception as e:
                    self.logger.error(f"Failed to load {season['number']}: {e}")
                    self.after(0, lambda s=season, err=e: messagebox.showerror("Error", f"Failed to load {s['number']}: {err}"))

            # Schedule UI update in main thread
            self.after(0, lambda: update_episode_list(all_episodes))

        def update_episode_list(all_episodes):
            for w in self.episode_frame.winfo_children():
                w.destroy()
            
            self.episode_vars = []
            for ep in all_episodes:
                var = tk.BooleanVar(value=True)
                chk = ctk.CTkCheckBox(self.episode_frame, text=F"S{ep['season']:02}E{ep['number']:02} - {ep['name']}", variable=var)
                chk.pack(anchor=tk.W, padx=5)
                self.episode_vars.append((var, ep))
            
            self.lbl_len_episodelist.configure(text=f"Selected Episode count: {len(all_episodes)}")
            if len(all_episodes) < len(self.master.file_list.get_children()):
                self.lbl_len_episodelist.configure(text_color="#ff0000")
            elif len(all_episodes) > len(self.master.file_list.get_children()):
                self.lbl_len_episodelist.configure(text_color="#ff7300")
            else:
                self.lbl_len_episodelist.configure(text_color="#ffffff")

        # Start the lookup in a separate thread to keep the UI responsive
        threading.Thread(target=load_episodes, args=(selected,), daemon=True).start()

    def _toggle_select(self):
        # Determine if we’re selecting or deselecting
        selecting_all = self.toggle.cget("text") == "Select All"

        # Toggle all season checkboxes
        for var, _ in self.season_vars:
            var.set(selecting_all)

        # Update button text
        if selecting_all:
            self.toggle.configure(text="Deselect All")
        else:
            self.toggle.configure(text="Select All")

        # Trigger episode list update
        self._on_season_select()
