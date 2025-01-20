import customtkinter as ctk
from tkinter import messagebox
import yaml
import os

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("Settings")
        self.geometry("600x600")
        self.resizable(False, False)
        
        # Make window modal
        self.transient(parent)
        self.grab_set()
        
        # Load configuration
        self.config_file = "config.yaml"
        self.config = self.load_config()
        
        self.create_widgets()
        
        # Center window
        self.center_window()
        
    def create_widgets(self):
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Model Configuration",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Create scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(
            main_frame,
            width=550,
            height=450,
            label_text="Model Settings",
            label_font=ctk.CTkFont(size=14)
        )
        self.scrollable_frame.pack(fill="both", expand=True)
        
        # Create input fields for all model environment variables
        self.env_entries = {}
        self.create_all_env_var_inputs()
        
        # Button area
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save_config,
            width=100
        )
        save_btn.pack(side="left", padx=5)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            width=100,
            fg_color="#666666",
            hover_color="#444444"
        )
        cancel_btn.pack(side="left", padx=5)
        
    def create_all_env_var_inputs(self):
        """Create input fields for all model environment variables"""
        try:
            for vendor in self.config.get("vendors", []):
                vendor_name = vendor.get("name", "")
                if not vendor_name:
                    continue
                    
                # Create vendor title
                vendor_label = ctk.CTkLabel(
                    self.scrollable_frame,
                    text=f"───── {vendor_name} ─────",
                    font=ctk.CTkFont(size=14, weight="bold")
                )
                vendor_label.pack(pady=(10, 5))
                
                for model in vendor.get("models", []):
                    model_name = model.get("name", "")
                    if not model_name:
                        continue
                        
                    # Create model title
                    model_frame = ctk.CTkFrame(self.scrollable_frame)
                    model_frame.pack(fill="x", pady=(5, 0), anchor="w")
                    
                    model_label = ctk.CTkLabel(
                        model_frame,
                        text=f"  {model_name}",
                        font=ctk.CTkFont(size=13)
                    )
                    model_label.pack(anchor="w")
                    
                    # Create environment variable input fields
                    for env_var in model.get("env_vars", []):
                        key = env_var.get("key", "")
                        value = env_var.get("value", "")
                        if not key:
                            continue
                            
                        frame = ctk.CTkFrame(model_frame)
                        frame.pack(fill="x", padx=20, pady=(5, 0))
                        
                        label = ctk.CTkLabel(
                            frame,
                            text=key,
                            width=200,
                            anchor="w"
                        )
                        label.pack(side="left")
                        
                        entry = ctk.CTkEntry(
                            frame,
                            placeholder_text=f"Enter {key}",
                            width=300
                        )
                        entry.pack(side="left", padx=10)
                        entry.insert(0, value)
                        
                        # Use model ID and environment variable key as unique identifier
                        self.env_entries[f"{model.get('model_id', '')}_{key}"] = entry
        except Exception as e:
            print(f"Error creating environment variable inputs: {str(e)}")
        
    def load_config(self):
        """Load configuration"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            except:
                return {"vendors": []}
        return {"vendors": []}
    
    def save_config(self):
        """Save configuration"""
        try:
            # Update environment variable values in configuration
            for vendor in self.config.get("vendors", []):
                for model in vendor.get("models", []):
                    model_id = model.get("model_id", "")
                    for env_var in model.get("env_vars", []):
                        key = env_var.get("key", "")
                        entry_key = f"{model_id}_{key}"
                        if entry_key in self.env_entries:
                            env_var["value"] = self.env_entries[entry_key].get().strip()
            
            # Save to file
            with open(self.config_file, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, allow_unicode=True, sort_keys=False)
            
            # Update environment variables
            self.update_environment_variables()
            
            self.destroy()
            messagebox.showinfo("Success", "Settings saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def update_environment_variables(self):
        """Update environment variables"""
        # Update environment variables for all models
        for vendor in self.config.get("vendors", []):
            for model in vendor.get("models", []):
                for env_var in model.get("env_vars", []):
                    key = env_var.get("key", "")
                    value = env_var.get("value", "")
                    if value:  # Only set non-empty values
                        os.environ[key] = value
            
    def center_window(self):
        """Center window in parent window"""
        self.update_idletasks()
        parent = self.master
        
        # Get parent and current window sizes
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Calculate center position
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        self.geometry(f"+{x}+{y}") 