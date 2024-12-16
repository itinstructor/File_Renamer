from base64 import b64decode
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from icons import ICON_16, ICON_32


class FileRenamer:
    def __init__(self, root):
        self.root = root
        self.root.title("File Renamer")
        self.root.geometry("800x600")

        small_icon = tk.PhotoImage(data=b64decode(ICON_16))
        large_icon = tk.PhotoImage(data=b64decode(ICON_32))
        self.root.iconphoto(False, large_icon, small_icon)
        self.create_widgets()

# ---------------------------- CREATE WIDGETS ---------------------------- #
    def create_widgets(self):
        # Directory selection frame
        dir_frame = ttk.Frame(self.root)
        dir_frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

        self.dir_path = tk.StringVar()
        dir_label = ttk.Label(dir_frame, text="Directory:")
        dir_label.grid(row=0, column=0, sticky="w")

        self.dir_entry = ttk.Entry(
            dir_frame, textvariable=self.dir_path, width=50)
        self.dir_entry.grid(row=0, column=1, padx=5, sticky="ew")

        dir_button = ttk.Button(dir_frame, text="Browse",
                                command=self.select_directory)
        dir_button.grid(row=0, column=2, sticky="e")

        dir_frame.columnconfigure(1, weight=1)

        # Options frame
        options_frame = ttk.Frame(self.root)
        options_frame.grid(row=1, column=0, pady=10, padx=10, sticky="ew")

        # Recursive search checkbox
        self.recursive_var = tk.BooleanVar(value=False)
        recursive_check = ttk.Checkbutton(
            options_frame, text="Recursive", variable=self.recursive_var)
        recursive_check.grid(row=0, column=0, sticky="w")

        # Rename folders checkbox
        self.rename_folders_var = tk.BooleanVar(value=False)
        rename_folders_check = ttk.Checkbutton(
            options_frame, text="Rename Folders", variable=self.rename_folders_var)
        rename_folders_check.grid(row=0, column=1, padx=10, sticky="w")

        # File type filter frame
        filter_frame = ttk.Frame(self.root)
        filter_frame.grid(row=2, column=0, pady=10, padx=10, sticky="ew")

        # File type filter label
        filter_label = ttk.Label(filter_frame, text="File Types:   ")
        filter_label.grid(row=0, column=0, sticky="w")

        # PDF checkbox
        self.pdf_var = tk.BooleanVar(value=False)
        pdf_check = ttk.Checkbutton(
            filter_frame, text=".pdf   ", variable=self.pdf_var)
        pdf_check.grid(row=0, column=1, sticky="w")

        # DOCX checkbox
        self.docx_var = tk.BooleanVar(value=False)
        docx_check = ttk.Checkbutton(
            filter_frame, text=".docx", variable=self.docx_var)
        docx_check.grid(row=0, column=2, sticky="w")

        # File list frame
        list_frame = ttk.Frame(self.root)
        list_frame.grid(row=3, column=0, pady=10, padx=10, sticky="nsew")

        # Treeview for file list with checkboxes
        self.file_tree = ttk.Treeview(list_frame, columns=(
            'filepath', 'filename', 'type', 'selected'), show='headings')
        self.file_tree.heading('filepath', text='Filepath',
                               command=lambda: self.sort_column('filepath', False))
        self.file_tree.heading('filename', text='Filename',
                               command=lambda: self.sort_column('filename', False))
        self.file_tree.heading('type', text='Type',
                               command=lambda: self.sort_column('type', False))
        self.file_tree.heading('selected', text='Selected',
                               command=lambda: self.sort_column('selected', False))
        self.file_tree.column('filepath', width=325)
        self.file_tree.column('filename', width=325)
        self.file_tree.column('type', width=50)
        self.file_tree.column('selected', width=50)
        self.file_tree.grid(row=0, column=0, sticky="nsew")

        # Dictionary to track sorting state for each column
        self.sort_order = {}
        for col in ('filepath', 'filename', 'type', 'selected'):
            # True for ascending, False for descending
            self.sort_order[col] = True

        # Scrollbar for file list
        scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.file_tree.configure(yscroll=scrollbar.set)

        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        # Bind double-click to toggle selection
        self.file_tree.bind('<Double-1>', self.toggle_item_selection)

        # Find and Replace frame
        find_frame = tk.Frame(self.root)
        find_frame.grid(row=4, column=0, pady=10, padx=10, sticky="ew")

        find_label = tk.Label(find_frame, text="Find:")
        find_label.grid(row=0, column=0, sticky="w")
        self.find_entry = tk.Entry(find_frame, width=20)
        self.find_entry.grid(row=0, column=1, padx=5, sticky="ew")

        replace_label = tk.Label(find_frame, text="Replace:")
        replace_label.grid(row=0, column=2, sticky="w")
        self.replace_entry = tk.Entry(find_frame, width=20)
        self.replace_entry.grid(row=0, column=3, padx=5, sticky="ew")

        find_frame.columnconfigure(1, weight=1)
        find_frame.columnconfigure(3, weight=1)

        # Additional replacement options frame
        replacement_frame = tk.Frame(self.root)
        replacement_frame.grid(row=5, column=0, pady=10, padx=10, sticky="ew")

        # Replace space checkbox
        self.replace_space_var = tk.BooleanVar(value=False)
        replace_space_check = tk.Checkbutton(
            replacement_frame, text="Replace Spaces", variable=self.replace_space_var)
        replace_space_check.grid(row=0, column=0, sticky="w")

        # Select All/Deselect All buttons
        select_all_button = tk.Button(
            replacement_frame, text="Select All", command=self.select_all_items)
        select_all_button.grid(row=0, column=1, padx=5, sticky="w")

        deselect_all_button = tk.Button(
            replacement_frame, text="Deselect All", command=self.deselect_all_items)
        deselect_all_button.grid(row=0, column=2, sticky="w")

        # Buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=6, column=0, pady=10, padx=10, sticky="ew")

        rename_button = tk.Button(
            button_frame, text="Rename Selected Items", command=self.rename_items)
        rename_button.grid(row=0, column=0, sticky="ew")

        button_frame.columnconfigure(0, weight=1)

        self.root.rowconfigure(3, weight=1)

# ------------------------------ SORT COLUMNS ---------------------------- #
    def sort_column(self, col, reverse):
        """
        Sort the treeview column

        :param col: Column to sort
        :param reverse: Whether to sort in reverse order
        """
        # Get the current list of items
        l = [(self.file_tree.set(k, col), k)
             for k in self.file_tree.get_children('')]

        # Sort the list
        try:
            # If column is numeric, sort numerically
            l.sort(key=lambda t: float(t[0]), reverse=reverse)
        except ValueError:
            # Otherwise, sort lexicographically
            l.sort(key=lambda t: t[0], reverse=reverse)

        # Rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            self.file_tree.move(k, '', index)

        # Toggle sort order for next time
        self.sort_order[col] = not reverse

# -------------------------- SELECT DIRECTORY ---------------------------- #
    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_path.set(directory)
            # Automatically load items when directory is selected
            self.load_items()

# ----------------------- IS FILE TYPE ALLOWED --------------------------- #
    def is_file_type_allowed(self, filename):
        """Check if file type is allowed based on selected checkboxes"""
        # If no file types are selected, show all files
        if not (self.pdf_var.get() or self.docx_var.get()):
            return True

        # Get file extension
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        # Check against selected file types
        if ext == '.pdf' and self.pdf_var.get():
            return True
        if ext == '.docx' and self.docx_var.get():
            return True

        return False

# ------------------------------ LOAD ITEMS ------------------------------ #
    def load_items(self):
        directory = self.dir_path.get()
        if not directory:
            messagebox.showerror("Error", "Please select a directory first.")
            return

        # Clear previous list
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        try:
            # List items recursively or non-recursively based on checkbox
            items_to_add = []
            if self.recursive_var.get():
                # Recursive search
                for root, dirs, files in os.walk(directory):
                    # Include folders if checkbox is checked
                    if self.rename_folders_var.get():
                        for dir_name in dirs:
                            full_path = os.path.join(root, dir_name)
                            rel_path = os.path.relpath(full_path, directory)
                            items_to_add.append(
                                (rel_path, dir_name, 'Folder', ''))

                    # Include files with type filtering
                    for file in files:
                        if self.is_file_type_allowed(file):
                            full_path = os.path.join(root, file)
                            rel_path = os.path.relpath(full_path, directory)
                            items_to_add.append((rel_path, file, 'File', ''))
            else:
                # Non-recursive search
                # Include folders if checkbox is checked
                if self.rename_folders_var.get():
                    dirs = [d for d in os.listdir(directory) if os.path.isdir(
                        os.path.join(directory, d))]
                    for dir_name in sorted(dirs):
                        items_to_add.append((dir_name, dir_name, 'Folder', ''))

                # Include files
                files = os.listdir(directory)
                for file in sorted(files):
                    full_path = os.path.join(directory, file)
                    if os.path.isfile(full_path) and self.is_file_type_allowed(file):
                        items_to_add.append((file, file, 'File', ''))

            # Sort items and add to treeview
            for filepath, filename, item_type, selected in items_to_add:
                self.file_tree.insert('', 'end', values=(
                    filepath, filename, item_type, selected))
        except Exception as e:
            messagebox.showerror("Error", f"Could not load items: {str(e)}")

# ------------------------ TOGGLE ITEM SELECTION ------------------------- #
    def toggle_item_selection(self, event):
        # Get the row that was clicked
        item = self.file_tree.identify_row(event.y)

        if item:
            # Toggle the selection
            current_values = self.file_tree.item(item, 'values')
            new_selection = '✓' if current_values[3] != '✓' else ''

            # Update the treeview
            self.file_tree.item(
                item, values=(
                    current_values[0],
                    current_values[1], current_values[2], new_selection)
            )

# ---------------------- SELECT ALL ITEMS -------------------------------- #
    def select_all_items(self):
        for item in self.file_tree.get_children():
            current_values = self.file_tree.item(item, 'values')
            self.file_tree.item(item, values=(
                current_values[0], current_values[1], current_values[2], '✓'))

# ---------------------- DESELECT ALL ITEMS ------------------------------ #
    def deselect_all_items(self):
        for item in self.file_tree.get_children():
            current_values = self.file_tree.item(item, 'values')
            self.file_tree.item(item, values=(
                current_values[0], current_values[1], current_values[2], ''))

# ------------------------ RENAME ITEMS ---------------------------------- #
    def rename_items(self):
        directory = self.dir_path.get()
        find_text = self.find_entry.get()
        replace_text = self.replace_entry.get()
        replace_spaces = self.replace_space_var.get()

        if not directory:
            messagebox.showerror("Error", "Please select a directory first.")
            return

        renamed_count = 0
        error_count = 0
        error_details = []

        # Ensure replace_text is not None
        if replace_text is None:
            replace_text = ''

        # Iterate through all items
        for item in self.file_tree.get_children():
            values = self.file_tree.item(item, 'values')

            # Check if item is selected
            if values[3] == '✓':
                # For recursive search, use the full relative path
                relative_path = values[0]
                old_filename = values[1]
                item_type = values[2]

                new_filename = old_filename

                # Replace specific text if find_text is provided
                if find_text:
                    new_filename = new_filename.replace(
                        find_text, replace_text)

                # Replace spaces if checkbox is checked
                if replace_spaces:
                    new_filename = new_filename.replace(' ', replace_text)

                # Only rename if filename actually changes
                if new_filename != old_filename:
                    try:
                        # For recursive search, construct full paths using the relative path
                        old_path = os.path.join(directory, relative_path)
                        new_path = os.path.join(
                            os.path.dirname(old_path), new_filename)

                        # Prevent overwriting existing files/folders
                        if os.path.exists(new_path):
                            raise FileExistsError(
                                f"{item_type} {new_filename} already exists")

                        os.rename(old_path, new_path)
                        renamed_count += 1
                    except Exception as e:
                        error_count += 1
                        error_details.append(
                            f"Error renaming {relative_path}: {str(e)}")

        # Refresh item list
        self.load_items()

        # Show summary with detailed error information
        if error_count > 0:
            detailed_error_msg = "\n".join(error_details)
            messagebox.showerror("Rename Errors",
                                 f"Renamed {renamed_count} items.\n"
                                 f"Errors encountered: {error_count}\n\n"
                                 f"Error Details:\n{detailed_error_msg}")
        else:
            messagebox.showinfo("Rename Complete",
                                f"Successfully renamed {renamed_count} items.")


def main():
    root = tk.Tk()
    app = FileRenamer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
