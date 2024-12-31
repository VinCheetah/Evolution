import os
import tkinter as tk
from tkinter import ttk, filedialog
import customtkinter as ctk

class EnhancedInterfaceFactory:
    def __init__(self, options_summary, default_opts):
        self.options_summary = options_summary
        self.default_opts = default_opts
        self.current_folder = None

        # Initialize UI
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.root = ctk.CTk()
        self.root.title("Enhanced Evopy Factory")

        # Create main layout
        self.nav_frame = ctk.CTkFrame(self.root)
        self.nav_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)

        self.details_frame = ctk.CTkFrame(self.root)
        self.details_frame.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)

        # Folder Tree Navigation
        self.tree = ttk.Treeview(self.nav_frame)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.populate_tree()
        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

        # Option Details
        self.details_label = ctk.CTkLabel(self.details_frame, text="Details")
        self.details_label.pack(anchor="w", padx=5, pady=5)

        self.option_widgets = {}
        self.details_container = ctk.CTkScrollableFrame(self.details_frame)
        self.details_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Save/Load Buttons
        self.save_button = ctk.CTkButton(self.root, text="Save Options", command=self.save_options)
        self.save_button.grid(row=1, column=0, sticky="we", padx=10, pady=5)

        self.load_button = ctk.CTkButton(self.root, text="Load Options", command=self.load_options)
        self.load_button.grid(row=1, column=1, sticky="we", padx=10, pady=5)

    def populate_tree(self):
        """Populate the tree view with folders and options."""
        for folder, options in self.options_summary.items():
            folder_node = self.tree.insert("", "end", text=folder, open=False)
            for option in options.keys():
                self.tree.insert(folder_node, "end", text=option)

    def on_tree_select(self, event):
        """Handle folder or option selection from the tree."""
        selected_item = self.tree.selection()
        if selected_item:
            item_text = self.tree.item(selected_item, "text")
            parent = self.tree.parent(selected_item)
            if parent:  # It's an option
                folder = self.tree.item(parent, "text")
                self.show_option_details(folder, item_text)

    def show_option_details(self, folder, option):
        """Display the details of an option for editing."""
        for widget in self.details_container.winfo_children():
            widget.destroy()

        self.details_label.configure(text=f"Editing: {folder} > {option}")
        option_data = self.options_summary[folder][option]

        for param, param_type in option_data.items():
            label = ctk.CTkLabel(self.details_container, text=f"{param} ({param_type.__name__}):")
            label.pack(anchor="w", padx=5, pady=2)

            if param_type == int:
                widget = ctk.CTkEntry(self.details_container)
            elif param_type == bool:
                widget = ctk.CTkCheckBox(self.details_container)
            elif param_type == str:
                widget = ctk.CTkEntry(self.details_container)
            elif isinstance(param_type, typing.Type):
                widget = ctk.CTkComboBox(self.details_container, values=[param_type.__name__])
            else:
                widget = ctk.CTkEntry(self.details_container)

            widget.pack(fill="x", padx=5, pady=2)
            self.option_widgets[param] = widget

    def save_options(self):
        """Save current options to a file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            # Implement saving logic here
            print("Options saved to", file_path)

    def load_options(self):
        """Load options from a file."""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            # Implement loading logic here
            print("Options loaded from", file_path)

    def run(self):
        self.root.mainloop()

# Example usage
if __name__ == "__main__":
    factory = EnhancedInterfaceFactory(options_summary, default_opts)
    factory.run()
