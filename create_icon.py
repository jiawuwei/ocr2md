from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # Create a square image
    size = 128  # Set size to 128x128
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Set colors
    primary_color = "#2196f3"  # Material Design blue
    
    # Draw circular background
    padding = 5  # Reduce padding
    draw.ellipse([padding, padding, size-padding, size-padding], fill=primary_color)
    
    # Draw OCR text
    try:
        # Try to load system font
        font_size = 50  # Adjust font size
        font = ImageFont.truetype("/System/Library/Fonts/STHeiti Light.ttc", font_size)
    except:
        # If system font not found, use default font
        font = ImageFont.load_default()
    
    text = "OCR"
    # Get text size
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Calculate text position for center alignment
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # Draw text
    draw.text((x, y), text, fill="white", font=font)
    
    # Ensure resources directory exists
    if not os.path.exists('resources'):
        os.makedirs('resources')
    
    # Save as PNG format only
    image.save("resources/icon.png", "PNG")

if __name__ == "__main__":
    create_icon() 