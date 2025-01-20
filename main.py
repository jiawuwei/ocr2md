import customtkinter as ctk
from gui import PDFConverterGUI
import os
import tkinter as tk

def center_window(window):
    """Center window on screen"""
    window.update_idletasks()  # Update window size
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def main():
    root = ctk.CTk()
    root.title("OCR")
    root.geometry("700x650")
    root.minsize(600, 500)
    
    # Set window icon
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
    if os.path.exists(icon_path):
        try:
            # Load icon using PhotoImage
            icon = tk.PhotoImage(file=icon_path)
            root.iconphoto(False, icon)
            # Keep icon reference
            root.icon = icon
        except Exception as e:
            print(f"Error loading icon: {e}")
    
    # Set window transparency
    root.attributes('-alpha', 0.95)
    
    # Center window on screen
    center_window(root)
    
    app = PDFConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 