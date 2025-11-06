import threading
import customtkinter as ctk
from tkinter import ttk, messagebox
from PIL import Image
from pathlib import Path

from core.config import Config, Logger
from core.utils import center_toscreen
from core.handbrake import HandBrake
from core.rules import apply_rule_to_path
from ui.menus import MainMenu, ToolBar
from ui.widgets import RuleList, CTkLabelFrame
from ui.dialogs.rule import RuleDialog
from ui.dialogs.episode import EpisodeMetadata
from ui.dialogs.import_csv import ImportCSVWizard
from ui.dialogs.progress import ProgressDialog
from ui.windows.settings import PreferencesWindow
from ui.windows.about import AboutWindow

class Application(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ctk.set_appearance_mode(
            Config.APPEARANCE_MODES[Config.get('UI Appearance')]['appearance_mode']
        )
        ctk.set_default_color_theme(
            Config.COLOR_THEMES[Config.get('UI Accent')]['color_mode']
        )
        # ----- Window Setup -----
        self.title(f"MetaMorph v{Config.VERSION}")
        self.geometry(center_toscreen(self, 1150, 800))
        self.iconbitmap(Config.WIN_ICO['mainwindow'])
        self.resizable(False, False)
        self.grab_set()
        
        # ----- Callbacks -----
        self.callbacks = {
            'add_files': self.add_files,
            'add_folder': self.add_folder,
            'remove_file': self.remove_file,
            'refresh_list': self.refresh_list,
            'clear_list': self.clear_list,
            'settings': self.open_settings,
            'about': self.open_about,
            'import_tv': self.import_tvshow,
            'import_csv_data': self.import_from_csv,
            'move_up': self.move_item_up,
            'move_down': self.move_item_down,
            'move_top': self.move_item_top,
            'move_bottom': self.move_item_bottom,
            'sort_ascend': lambda: self.sort_filelist(reversed=False),
            'sort_descend': lambda: self.sort_filelist(reversed=True),
            'override_name': self.override_filename,
        }
        # ----- Attributes -----
        self.btn_imgs = {
            'start_batch': ctk.CTkImage(light_image=Image.open(Config.BTN_IMGS['start_batch']),
                                        dark_image=Image.open(Config.BTN_IMGS['start_batch']),
                                        size=(32, 32)),
        }
        self.logger = Logger.get_logger(__name__)
        self.files = []
        self.overrides = {}
        self.rules = []
        self.tv_metadata = {}
        self.csv_metadata = {}

        self.build_ui()

    def build_ui(self):
        # ----- Main Menu -----
        main_menu = MainMenu(self, self.callbacks)
        self.config(menu=main_menu)
        # ----- Toolbar -----
        ToolBar(self, self.callbacks, border_width=2).pack(side='top', fill='x')
        # ----- Top Frame -----
        top_frame = ctk.CTkFrame(self)
        ctk.CTkButton(top_frame, text="Start Batch", image=self.btn_imgs['start_batch'], compound='right',
                      command=self.start_batch).pack(side='right', padx=10, pady=10)
        top_frame.pack(fill='x', pady=5)
        # ----- Main Content Area -----
        content_frame = ctk.CTkFrame(self)
        rule_frame = CTkLabelFrame(content_frame, label="  Renaming Rules:", font=ctk.CTkFont(size=10, weight='bold'), label_bg="#95a5a6")
        self.rule_list = RuleList(rule_frame, self.edit_rule, self.remove_rule)
        self.rule_list.pack(fill='both', expand=True)
        rbtn_frame = ctk.CTkFrame(rule_frame)
        ctk.CTkButton(rbtn_frame, text="Add", width=50, command=self.add_rule).pack(side='left', padx=2, pady=5)
        ctk.CTkButton(rbtn_frame, text="Edit", width=50, command=self.edit_rule).pack(side='left', padx=2, pady=5)
        ctk.CTkButton(rbtn_frame, text="Remove", width=50, command=self.remove_rule).pack(side='left', padx=2, pady=5)
        rbtn_frame.pack(side='bottom', fill='x')
        rule_frame.pack(side='left', fill='y', padx=5)
        content_frame.pack(fill='both', expand=True, padx=5, pady=5)
        # ----- File List Table -----
        flst_frame = CTkLabelFrame(content_frame, label="  Files / Folders", font=ctk.CTkFont(size=10, weight='bold'),
                     label_bg="#95a5a6")
        style = ttk.Style()
        style.theme_use('winnative')
        style.configure("Treeview", background="#343638", foreground="#FFFFFF", fieldbackground="#343638",
                        font=('Arial',12), rowheight=35)
        style.map('Treeview', background=[('selected', '#2B2B2B')], foreground=[('selected', "#FFFFFF")])
        self.file_list = ttk.Treeview(flst_frame, columns=("Filename", "New Filename", "Status"), show='headings',
                                      selectmode='extended')
        self.file_list.heading("Filename", text="Filename")
        self.file_list.heading("New Filename", text="New Filename")
        self.file_list.heading("Status", text="Status")
        self.file_list.column("Filename", width=300)
        self.file_list.column("New Filename", width=300)
        self.file_list.column("Status", width=100)
        self.file_list.tag_configure('overridden', foreground='#0018d2')
        self.file_list.bind("<Button-3>", self._file_list_context_menu)
        self.file_list.pack(fill='both', expand=True)
        flst_frame.pack(side='right', fill='both', expand=True)
        # ----- Status Bar -----
        self.status_bar = ctk.CTkLabel(self, text="Ready", height=20, anchor='w', font=ctk.CTkFont(size=10), bg_color="#3c3e3e")
        self.status_bar.pack(side='bottom', fill='x')

    # ---------------
    # File List Management
    # ---------------
    def add_files(self):
        paths = ctk.filedialog.askopenfilenames(title="Select Files")
        for p in paths:
            if Path(p) not in self.files:
                self.files.append(Path(p))
        self.logger.info("Files added to file list.")
        self.refresh_list()
    
    def add_folder(self):
        folder = ctk.filedialog.askdirectory(title="Select Folder")
        if not folder:
            return
        for p in Path(folder).rglob('*'):
            if p.isfile() and p not in self.files:
                self.files.append(p)
        self.logger.info("Files added to file list.")
        self.refresh_list()
    
    def remove_file(self):
        selected = self.file_list.selection()
        if not selected:
            return
        
        for item in selected:
            values = self.file_list.item(item, "values")
            if values:
                filename = values[0]
                # remove from self.files as well
                self.files = [f for f in self.files if f.name != filename]
            self.file_list.delete(item)
        self.logger.info("File(s) removed to file table")

    def refresh_list(self):
        for row in self.file_list.get_children():
            self.file_list.delete(row)
        for i, p in enumerate(self.files):
            try:
                new_path = self._apply_rules_in_sequence(p, index=i)
                status = "Pending" if not new_path.exists() or new_path == p else "Collision"
                self.file_list.insert('', 'end', values=(p.name, new_path.name, status))
            except Exception as e:
                self.file_list.insert('', 'end', values=(p.name, new_path.name, f"Error: {e}"))
                self.logger.error(f"Encountered error: {e}")
        
        self.status_bar.configure(text=f"Preview refreshed. {len(self.files)} items")

    def clear_list(self):
        self.files.clear()
        self.refresh_list()
        self.logger.info("file table cleared")

    def move_item_up(self):
        selected = self.file_list.selection()
        for item in selected:
            prev_item = self.file_table.prev(item)
            if prev_item:
                self.file_table.move(item, self.file_table.parent(prev_item), self.file_table.index(prev_item))
        
        self._sync_file_from_table()

    def move_item_down(self):
        selected = self.file_list.selection()
        for item in reversed(selected):
            next_item = self.file_list.next(item)
            if next_item:
                self.file_list.move(item, self.file_table.parent(next_item), self.file_table.index(next_item))
        
        self._sync_file_from_table()

    def move_item_top(self):
        selected = self.file_list.selection()
        if not selected:
            return
        
        # Collect items in the order that they were selected
        selected_items = list(selected)

        # Move each selected item to the top (one by one)
        for item in selected_items:
            self.file_list.move(item, "", 0)

        self._sync_file_from_table()

    def move_item_bottom(self):
        selected = self.file_list.selection()
        if not selected:
            return
        
        # Collect items in the order that they were selected
        selected_items = list(selected)

        # Move each selected item to the bottom (one by one)
        for item in selected_items:
            self.file_list.move(item, "", "end")

        self._sync_file_from_table()

    def sort_filelist(self, reversed=False):
        # Grab all items and their values
        items = [(self.file_list.item(i, "values"), i) for i in self.file_table.get_children()]
        # Sort by filename (first column), normal or reversed
        items.sort(key=lambda x: x[0][0].lower(), reverse=reversed)
        # Reinsert rows in sorted order
        for index, (vals, iid) in enumerate(items):
            self.file_list.move(iid, "", index)

        # Keep self.files in sync with Treeview
        new_files = []
        for vals, iid in items:
            filename = vals[0]
            for f in self.files:
                if f.name == filename:
                    new_files.append(f)
                    break
        self.files = new_files

    def override_filename(self):
        """Prompt for a new filename and store it for deferred rename."""
        from ...ui.dialogs.override import OverrideDialog

        item_id = self.file_list.selection()
        if not item_id:
            return
        item_id = item_id[0]

        vals = list(self.file_list.item(item_id, 'values'))
        orig_name = vals[0]
        current_preview = vals[1]

        dlg = OverrideDialog(self, title="Override Filename", prompt="Enter new filename", initialvalue=current_preview)
        self.wait_window(dlg)
        new_name = dlg.result
        if not new_name or new_name.strip() == "":
            return
        
        # Preserve extension if user omits it
        orig_ext = Path(orig_name).suffix
        if "." not in new_name:
            new_name = f"{new_name}{orig_ext}"

        # Record deferred override
        self.overrides[orig_name] = new_name

        # Update preview in the Treeview only
        vals[1] = new_name
        self.file_list.item(item_id, values=vals)
        self.file_list.item(item_id, tags=("overridden",))
        self.logger.info(f"Deferred rename queued: {orig_name} → {new_name}")

    def _apply_rules_in_sequence(self, path: Path, index: int = 0) -> Path:
        current = path
        seqnum = None
        # Merge metadata sources: first TV metadata, then CSV metadata (CSV overrides TV if same key)
        metadata = {}
        if hasattr(self, 'tv_metadata') and isinstance(self.tv_metadata, dict):
            metadata.update(self.tv_metadata.get(path.name, {}))
        if hasattr(self, 'csv_metadata') and isinstance(self.csv_metadata, dict):
            metadata.update(self.csv_metadata.get(path.name, {}))

        for r in self.rules:
            if not r.enabled:
                continue
            if r.type.lower() == "numbering":
                start = int(r.params.get("start", 1))
                inc = int(r.params.get("increment", 1))
                seqnum = start + index * inc
            current = apply_rule_to_path(r, current, seqnum, metadata=metadata)
        return current

    def _sync_file_from_table(self):
        """Rebuild self.files based on Treeview order."""
        new_files = []
        for item in self.file_list.get_children():
            filename = self.file_list.item(item, "values")[0]
            for f in self.files:
                if f.name == filename:
                    new_files.append(f)
                    break
        self.files = new_files

    def _file_list_context_menu(self, event):
        from ...ui.menus import FileContextMenu

        context = FileContextMenu(self, self.callbacks)
        # ----- Identify clicked row -----
        row_id = self.file_list.identify_row(event.y)
        if row_id:
            self.file_list.selection_set(row_id)
            context.tk_popup(event.x_root, event.y_root)
        else:
            context.unpost()
    
    # ---------------
    # Rule Management
    # ---------------
    def add_rule(self):
        dlg = RuleDialog(self); self.wait_window(dlg)
        if dlg.result:
            print(f"DEBUG: result of RuleDialog: {dlg.result}")
            self.rules.append(dlg.result)
            self.rule_list.refresh(self.rules)
            self.refresh_list()

    def edit_rule(self, idx):
        dlg = RuleDialog(self, existing=self.rules[idx]); self.wait_window(dlg)
        if dlg.result_rule:
            self.rules[idx] = dlg.result_rule
            self.rule_list.refresh(self.rules)
            self.refresh_list()
        
    def remove_rule(self, idx):
        del self.rules[idx]
        self.rule_list.refresh(self.rules)
        self.refresh_list()

    # ---------------
    # Metadata Importing
    # ---------------
    def import_tvshow(self):
        dlg = EpisodeMetadata(self)
        if dlg.selected_show and dlg.selected_episodes:
            show = dlg.selected_show
            for i, ep in enumerate(dlg.selected_episodes):
                if i < len(self.files):
                    file = self.files[i]
                    self.tv_metadata[file.name] = {
                        "show": show['name'],
                        "season": ep['season'],
                        "year": show.get('premiered', 'N/A')[:4] if show.get('premiered') else 'N/A',
                        "episode": ep['number'],
                        "title": ep['name'],
                    }
            messagebox.showinfo("Info", f"Imported {len(dlg.selected_episodes)} episodes from '{show['name']}'")
            self.logger.info(f"Imported {len(dlg.selected_episodes)} episodes from '{show['name']}'")
        self.refresh_list()

    def import_from_csv(self):
        dlg = ImportCSVWizard(self)
        self.wait_window(dlg)
        if not dlg.data:
            return

        # Map CSV rows to files by index: file i gets CSV row i (if present)
        # Store as dict keyed by filename for easy lookup later
        self.csv_metadata = {}
        for i, row in enumerate(dlg.data):
            if i < len(self.files):
                file = self.files[i]
                self.csv_metadata[file.name] = row

        messagebox.showinfo('Import Complete', f'Imported {len(dlg.data)} rows; mapped to {len(self.csv_metadata)} files.')
        self.logger.info(f'Imported {len(dlg.data)} rows; mapped to {len(self.csv_metadata)} files.')
        self.refresh_list()

    # ---------------
    # Batch Processing
    # ---------------
    def start_batch(self):
        if not self.files:
            messagebox.showwarning("Warning", "No files to process.")
            self.logger.error("No files to process")
            return
        
        dlg = ProgressDialog(self, title="Batch Progress", message="Transcoding files...")
        self.hb = HandBrake()
        total_files = len(self.files)

        def process_next_file(idx=0):
            # run entirely in a background thread
            if dlg.canceled or idx >= total_files:
                # ensure hb subprocess is terminated if running
                if self.hb.process and self.hb.process.poll() is None:
                    try:
                        self.hb.process.terminate()
                    except Exception:
                        pass
                self.overrides.clear()
                # schedule dialog destroy and status update on main thread
                def finish_gui():
                    if dlg.winfo_exists():
                        dlg.destroy()
                    self.status_bar.configure(text="Batch canceled" if dlg.canceled else "Batch finished")
                self.after(0, finish_gui)
                return

            file = self.files[idx]
            # --- Apply deferred override if one exists ---
            orig_name = file.name
            if hasattr(self, "overrides") and orig_name in self.overrides:
                override_name = self.overrides[orig_name]
                # Preserve extension if user forgot it
                if "." not in override_name:
                    override_name += file.suffix
                new_path = file.parent / override_name
                self.logger.info(f"Applying deferred override for {orig_name} → {override_name}")
            else:
                # Fall back to standard rule-based rename
                new_path = self._apply_rules_in_sequence(file, index=idx)

            # Rename/move original file to new name
            try:
                renamed_file = file.parent / new_path.name
                if file != renamed_file:
                    file.rename(renamed_file)
                # update stored path to the renamed Path
                self.files[idx] = renamed_file
                input_path_for_hb = str(self.files[idx])
            except Exception as e:
                # schedule error message and continue with next file
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to rename {file}: {e}"))
                self.logger.error(f"Failed to rename {file}: {e}")
                # start next file in a new background thread
                threading.Thread(target=process_next_file, args=(idx + 1,), daemon=True).start()
                return

            def on_progress(percent, input_file):
                # schedule GUI update
                dlg.after(0, lambda: dlg.update_progress(percent, message=f"Processing: {input_file}"))

                # update the status to show spinner (⏳) for current file
                for item in self.file_list.get_children():
                    values = self.file_list.item(item, "values")
                    if values and values[0] == Path(input_file).name:
                        self.file_list.set(item, column="Status", value="⏳")
                        break

            def on_done(success, input_file, output_file, cancelled=False):
                # schedule GUI update on main thread, then start next file in background
                def gui_update():
                    name = Path(input_file).name if input_file else "(unknown)"
                    if success:
                        self.status_bar.configure(text=f"Done: {name}")
                    elif cancelled:
                        self.status_bar.configure(text=f"Cancelled: {name}")
                    else:
                        self.status_bar.configure(text=f"Failed: {name}")
                    
                    # update the status in the table
                    for item in self.file_list.get_children():
                        values = self.file_list.item(item, "values")
                        if values and values[0] == Path(input_file).name:
                            self.file_list.set(item, column="Status", value="✅")
                            break

                    # update total progress display
                    if dlg.winfo_exists():
                        pcnt = float(((idx + 1) / total_files) * 100)
                        print(f"DEBUG: total_percent: {pcnt:2f}%")
                        dlg.total_progress.set(pcnt / 100)
                        dlg.total_text.set(f"{pcnt:.2f}%")

                    # start next file in a new worker thread (NOT on GUI thread)
                    if not dlg.canceled:
                        threading.Thread(target=process_next_file, args=(idx + 1,), daemon=True).start()
                    else:
                        # if canceled, ensure hb subprocess terminated and close dialog
                        if self.hb.process and self.hb.process.poll() is None:
                            try:
                                self.hb.process.terminate()
                            except Exception:
                                pass
                        if dlg.winfo_exists():
                            dlg.destroy()
                self.after(0, gui_update)

            # Run HandBrake in this worker thread (blocks this thread only)
            self.hb.transcode(
                input_path_for_hb,
                Config.get("Output Directory"),
                progress_callback=on_progress,
                done_callback=on_done,
                del_original=Config.get("Delete Original"),
                cancel_flag=lambda: dlg.canceled
            )
        self.logger.info("Processing next file")
        # start the first file in a background thread and let the GUI loop run
        threading.Thread(target=process_next_file, args=(0,), daemon=True).start()
        dlg.wait_window()
        
    # ---------------
    # Settings Management
    # ---------------
    def open_settings(self):
        PreferencesWindow(self)
        
    def open_about(self):
        AboutWindow(self)
