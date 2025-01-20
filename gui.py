import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from converter import PDFConverterTool
import os
import asyncio
import threading
import logging
from datetime import datetime
import yaml

# Configure logging
def setup_logger():
    # Create logs directory
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Generate log filename with timestamp
    log_filename = os.path.join('logs', f'pdf_converter_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    # Configure log format
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # Output to console as well
        ]
    )
    return logging.getLogger(__name__)

class PDFConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR2MD")
        self.root.geometry("800x600")
        
        # Initialize converter
        self.converter = PDFConverterTool()
        
        # Initialize variables
        self.input_path = None
        self.is_converting = False
        self.default_model_set = False
        
        # Setup styles
        self.bg_color = '#f5f5f5'  # Light gray background
        self.card_bg = '#ffffff'   # White card background
        self.text_color = '#333333'  # Dark text
        self.secondary_text = '#666666'  # Secondary text
        self.error_color = '#ff4757'  # Error color
        self.button_color = '#2d7aff'  # 蓝色按钮
        self.button_hover_color = '#1e6bff'  # 深蓝色悬停
        
        # Create widgets
        self.create_widgets()
        
        # Center window
        self.center_window()
        
        # Initialize logger
        self.logger = setup_logger()
        self.logger.info("OCR started")
        
    def create_widgets(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self.root, fg_color=self.bg_color, border_width=0)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # File selection area
        self.file_frame = ctk.CTkFrame(self.main_frame, fg_color=self.bg_color, border_width=0)
        self.file_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.file_entry = ctk.CTkEntry(self.file_frame, border_width=1, fg_color=self.bg_color)
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
        self.file_entry.insert(0, "Select file to convert...")
        self.file_entry.configure(state="readonly")
        
        self.file_btn = ctk.CTkButton(
            self.file_frame,
            text="Browse",
            command=self.select_file,
            fg_color=self.button_color,
            hover_color=self.button_hover_color
        )
        self.file_btn.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Configuration options area
        self.options_frame = ctk.CTkFrame(self.main_frame, fg_color=self.bg_color, border_width=0)
        self.options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Model selection
        self.model_frame = ctk.CTkFrame(self.options_frame, border_width=0, fg_color=self.card_bg)
        self.model_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.model_label = ctk.CTkLabel(self.model_frame, text="Model:", fg_color=self.card_bg)
        self.model_label.pack(side=tk.LEFT)
        
        # Get model list
        model_list = self.converter.get_model_list()
        
        # Create model dropdown
        self.model_var = tk.StringVar()
        self.model_menu = ctk.CTkOptionMenu(
            self.model_frame,
            values=model_list,
            command=self.on_model_select,
            height=40,
            font=ctk.CTkFont(size=13),
            dropdown_font=ctk.CTkFont(size=13),
            width=300,
            dynamic_resizing=False,
            fg_color=self.button_color,
            button_color=self.button_color,
            button_hover_color=self.button_hover_color,
            dropdown_fg_color=self.card_bg,
            dropdown_hover_color="#eef3ff",
            dropdown_text_color=self.text_color,
            text_color="#ffffff"
        )
        self.model_menu.pack(side=tk.LEFT, padx=(5, 0))
        
        # Set default model
        for item in model_list:
            if not item.startswith("─────"):
                self.model_menu.set(item)
                model_id = self.converter.model_map.get(item, "")
                if model_id:
                    self.model_var.set(item)
                    self.converter.set_current_model(model_id)
                    self.default_model_set = True
                    print(f"Default model set to: {item}")
                    break
                    
        if not self.default_model_set:
            print("Warning: No default model set")
        
        # Page selection
        self.page_frame = ctk.CTkFrame(self.options_frame, border_width=0, fg_color=self.card_bg)
        self.page_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.page_label = ctk.CTkLabel(self.page_frame, text="Pages:", fg_color=self.card_bg)
        self.page_label.pack(side=tk.LEFT)
        
        self.page_entry = ctk.CTkEntry(self.page_frame, fg_color=self.card_bg)
        self.page_entry.pack(side=tk.LEFT, padx=(5, 0))
        self.page_entry.insert(0, "Example: 1,2,3 or 1-5 or leave empty for all")
        
        # Button area
        self.button_frame = ctk.CTkFrame(self.main_frame, border_width=0, fg_color=self.bg_color)
        self.button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Left buttons
        self.left_btn_frame = ctk.CTkFrame(self.button_frame, border_width=0, fg_color=self.bg_color)
        self.left_btn_frame.pack(side=tk.LEFT)
        
        self.start_btn = ctk.CTkButton(
            self.left_btn_frame,
            text="Start Convert",
            command=self.start_convert,
            fg_color=self.button_color,
            hover_color=self.button_hover_color
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_btn = ctk.CTkButton(
            self.left_btn_frame,
            text="Stop Convert",
            command=self.stop_convert,
            state="disabled",
            fg_color="#9e9e9e",
            hover_color=self.error_color
        )
        self.stop_btn.pack(side=tk.LEFT)
        
        # Status display area
        self.status_frame = ctk.CTkFrame(self.main_frame, fg_color=self.card_bg, border_width=0)
        self.status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = ctk.CTkTextbox(
            self.status_frame,
            wrap="word",
            height=180,
            font=ctk.CTkFont(size=13),
            border_width=0,
            fg_color=self.card_bg
        )
        self.status_text.pack(fill="both", expand=True, padx=0, pady=0)
        
    def select_file(self):
        """Handle file selection"""
        filetypes = [
            ("All Supported Files", ("*.pdf", "*.doc", "*.docx", "*.odt", "*.ott", "*.rtf", "*.txt",
                                   "*.html", "*.htm", "*.xml", "*.wps", "*.wpd", "*.xls", "*.xlsx",
                                   "*.ods", "*.ots", "*.csv", "*.tsv", "*.ppt", "*.pptx", "*.odp",
                                   "*.otp", "*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.tiff",
                                   "*.webp")),
            ("PDF Files", "*.pdf"),
            ("Word Documents", ("*.doc", "*.docx", "*.odt", "*.ott", "*.rtf", "*.txt", "*.wps", "*.wpd")),
            ("Excel Files", ("*.xls", "*.xlsx", "*.ods", "*.ots", "*.csv", "*.tsv")),
            ("PowerPoint Files", ("*.ppt", "*.pptx", "*.odp", "*.otp")),
            ("Web Documents", ("*.html", "*.htm", "*.xml")),
            ("Image Files", ("*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.tiff", "*.webp")),
            ("All Files", "*.*")
        ]
        
        try:
            filepath = filedialog.askopenfilename(
                parent=self.root,
                title="Select File to Convert",
                filetypes=filetypes
            )
            
            if filepath:
                self.input_path = filepath
                self.file_entry.configure(state="normal")
                self.file_entry.delete(0, tk.END)
                self.file_entry.insert(0, filepath)
                self.file_entry.configure(state="readonly")
                self.logger.info(f"Selected file: {filepath}")
        except Exception as e:
            self.logger.error(f"Error selecting file: {str(e)}")
            messagebox.showerror("Error", f"Failed to select file: {str(e)}")
            
    def set_converting_state(self, is_converting):
        """Update UI state during conversion"""
        self.is_converting = is_converting
        
        if is_converting:
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(
                state="normal",
                fg_color=self.error_color,
                hover_color="#d32f2f"
            )
            self.file_btn.configure(state="disabled")
        else:
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(
                state="disabled",
                fg_color="#9e9e9e",
                hover_color="#d32f2f"
            )
            self.file_btn.configure(state="normal")
            
    def update_status(self, message, level="info"):
        """Update status text area"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        
    def show_settings(self):
        """Show settings dialog"""
        from settings import SettingsDialog
        dialog = SettingsDialog(self.root)
        self.root.wait_window(dialog)  # Wait for dialog to close
        
        # Update environment variables
        if hasattr(dialog, 'settings'):
            for key, value in dialog.settings.items():
                if value:  # Only set non-empty values
                    os.environ[key] = value 
        
    def on_model_select(self, display_name):
        """Handle model selection"""
        if display_name.startswith("─────"):
            return
            
        model_id = self.converter.model_map.get(display_name, "")
        if model_id:
            self.model_var.set(display_name)
            self.converter.set_current_model(model_id)
            
    def start_convert(self):
        """Start conversion process"""
        if not self.input_path:
            messagebox.showerror("Error", "Please select a file to convert")
            return
            
        # Get selected pages
        pages = self.page_entry.get().strip()
        select_pages = None
        if pages and pages != "Example: 1,2,3 or 1-5 or leave empty for all":
            try:
                # Parse page numbers
                select_pages = []
                # Split by comma and handle each part
                parts = [p.strip() for p in pages.split(',')]
                for part in parts:
                    if '-' in part:
                        # Handle range format (e.g. 1-5)
                        start, end = map(int, part.split('-'))
                        select_pages.extend(list(range(start, end + 1)))
                    else:
                        # Handle single page number
                        select_pages.append(int(part))
                self.logger.info(f"Parsed pages: {select_pages}")
            except ValueError:
                messagebox.showerror("Error", "Invalid page format")
                return
            
        # Start conversion
        self.set_converting_state(True)
        self.update_status("Starting conversion...")
        
        # Run conversion in thread
        threading.Thread(
            target=lambda: asyncio.run(self.run_conversion(self.input_path, select_pages)),
            daemon=True
        ).start()
        
    def stop_convert(self):
        """Stop conversion process"""
        self.is_converting = False
        self.update_status("Conversion stopped by user")
        self.set_converting_state(False)
        
    async def run_conversion(self, input_path, pages=None):
        """Run conversion process"""
        try:
            # Log conversion parameters
            self.logger.info("\n=== Zerox Conversion Parameters ===")
            self.logger.info(f"Input file: {input_path}")
            self.logger.info(f"Output directory: {self.converter.get_downloads_dir()}")
            self.logger.info(f"Selected pages: {pages}")
            self.logger.info(f"Model ID: {self.converter.current_model_id}")
            self.logger.info("================================\n")
            
            # Check if file needs conversion to PDF
            file_ext = os.path.splitext(input_path)[1].lower().lstrip('.')
            need_pdf_conversion = file_ext in [
                "doc", "docx", "odt", "ott", "rtf", "txt", "html", "htm", 
                "xml", "wps", "wpd", "xls", "xlsx", "ods", "ots", "csv", 
                "tsv", "ppt", "pptx", "odp", "otp", "jpg", "jpeg", "png", 
                "gif", "bmp", "tiff", "webp"
            ]
            
            if need_pdf_conversion:
                self.logger.info(f"Converting {file_ext} file to PDF...")
                self.update_status(f"Converting {file_ext} file to PDF...")
                try:
                    input_path = await self.converter.convert_to_pdf(input_path)
                    self.logger.info(f"File converted to PDF: {input_path}")
                    self.update_status("File converted to PDF successfully")
                except Exception as e:
                    self.logger.error(f"PDF conversion failed: {str(e)}")
                    self.update_status(f"PDF conversion failed: {str(e)}", "error")
                    return
            
            success, result = await self.converter.convert_file(
                input_path,
                pages=pages
            )
            
            if success:
                self.update_status(f"Conversion completed: {result}")
            else:
                self.update_status(f"Conversion failed: {result}", "error")
                
        except Exception as e:
            self.update_status(f"Error: {str(e)}", "error")
            
        finally:
            self.set_converting_state(False)
            
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}") 