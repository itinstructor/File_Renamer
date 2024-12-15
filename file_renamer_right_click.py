import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class FileRenamer:
    def __init__(self, master):
        self.master = master
        master.title("File Renamer")
        master.geometry("600x550")

        # Directory selection frame
        dir_frame = tk.Frame(master)
        dir_frame.pack(pady=10, padx=10, fill=tk.X)

        self.dir_path = tk.StringVar()
        dir_label = tk.Label(dir_frame, text="Directory:")
        dir_label.pack(side=tk.LEFT)

        dir_entry = tk.Entry(dir_frame, textvariable=self.dir_path, width=50)
        dir_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        dir_button = tk.Button(dir_frame, text="Browse",
                               command=self.select_directory)
        dir_button.pack(side=tk.RIGHT)

        # File list frame
        list_frame = tk.Frame(master)
        list_frame.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)

        # Treeview for file list with checkboxes
        self.file_tree = ttk.Treeview(list_frame, columns=(
            'filename', 'selected'), show='headings')
        self.file_tree.heading('filename', text='Filename')
        self.file_tree.heading('selected', text='Selected')
        self.file_tree.column('filename', width=450)
        self.file_tree.column('selected', width=50, anchor='center')
        self.file_tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Scrollbar for file list
        scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_tree.configure(yscroll=scrollbar.set)

        # Bind right-click for selection
        self.file_tree.bind('<Button-3>', self.toggle_file_selection)

        # Find and Replace frame
        find_frame = tk.Frame(master)
        find_frame.pack(pady=10, padx=10, fill=tk.X)

        find_label = tk.Label(find_frame, text="Find:")
        find_label.pack(side=tk.LEFT)
        self.find_entry = tk.Entry(find_frame, width=20)
        self.find_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        replace_label = tk.Label(find_frame, text="Replace:")
        replace_label.pack(side=tk.LEFT)
        self.replace_entry = tk.Entry(find_frame, width=20)
        self.replace_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # Special replacement options frame
        options_frame = tk.Frame(master)
        options_frame.pack(pady=10, padx=10, fill=tk.X)

        # Replace space checkbox
        self.replace_space_var = tk.BooleanVar(value=False)
        replace_space_check = tk.Checkbutton(options_frame, text="Replace Spaces",
                                             variable=self.replace_space_var)
        replace_space_check.pack(side=tk.LEFT)

        # Select All/Deselect All buttons
        select_all_button = tk.Button(
            options_frame, text="Select All", command=self.select_all_files)
        select_all_button.pack(side=tk.LEFT, padx=5)

        deselect_all_button = tk.Button(
            options_frame, text="Deselect All", command=self.deselect_all_files)
        deselect_all_button.pack(side=tk.LEFT)

        # Buttons frame
        button_frame = tk.Frame(master)
        button_frame.pack(pady=10, padx=10, fill=tk.X)

        load_files_button = tk.Button(
            button_frame, text="Load Files", command=self.load_files)
        load_files_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        rename_button = tk.Button(
            button_frame, text="Rename Selected Files", command=self.rename_files)
        rename_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_path.set(directory)

    def load_files(self):
        directory = self.dir_path.get()
        if not directory:
            messagebox.showerror("Error", "Please select a directory first.")
            return

        # Clear previous list
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        try:
            # List and add files to treeview
            files = os.listdir(directory)
            for file in sorted(files):
                self.file_tree.insert('', 'end', values=(file, ''))
        except Exception as e:
            messagebox.showerror("Error", f"Could not load files: {str(e)}")

    def toggle_file_selection(self, event):
        # Get the row that was clicked
        item = self.file_tree.identify_row(event.y)

        if item:
            # Toggle the selection
            current_values = self.file_tree.item(item, 'values')
            new_selection = '✓' if current_values[1] != '✓' else ''

            # Update the treeview
            self.file_tree.item(item, values=(
                current_values[0], new_selection))

    def select_all_files(self):
        for item in self.file_tree.get_children():
            current_values = self.file_tree.item(item, 'values')
            self.file_tree.item(item, values=(current_values[0], '✓'))

    def deselect_all_files(self):
        for item in self.file_tree.get_children():
            current_values = self.file_tree.item(item, 'values')
            self.file_tree.item(item, values=(current_values[0], ''))

    def rename_files(self):
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

            # Check if file is selected
            if values[1] == '✓':
                old_filename = values[0]
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
                        old_path = os.path.join(directory, old_filename)
                        new_path = os.path.join(directory, new_filename)

                        # Prevent overwriting existing files
                        if os.path.exists(new_path):
                            raise FileExistsError(
                                f"File {new_filename} already exists")

                        os.rename(old_path, new_path)
                        renamed_count += 1
                    except Exception as e:
                        error_count += 1
                        error_details.append(
                            f"Error renaming {old_filename}: {str(e)}")

        # Refresh file list
        self.load_files()

        # Show summary with detailed error information
        if error_count > 0:
            detailed_error_msg = "\n".join(error_details)
            messagebox.showerror("Rename Errors",
                                 f"Renamed {renamed_count} files.\n"
                                 f"Errors encountered: {error_count}\n\n"
                                 f"Error Details:\n{detailed_error_msg}")
        else:
            messagebox.showinfo("Rename Complete",
                                f"Successfully renamed {renamed_count} files.")


def main():
    root = tk.Tk()
    app = FileRenamer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
