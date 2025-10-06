#!/usr/bin/env python3
"""
Create a placeholder image for songs without artwork.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_image(output_path="data/artwork/placeholder.jpg", size=(200, 200)):
    """Create a simple placeholder image for songs without artwork."""
    
    # Create a new image with a dark background
    img = Image.new('RGB', size, color='#333333')
    draw = ImageDraw.Draw(img)
    
    # Try to use a system font, fallback to default if not available
    try:
        # Try to load a nice font
        font_size = size[0] // 8
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.load_default()
        except:
            font = None
    
    # Draw a music note symbol and text
    text = "♪\nNo Artwork"
    
    # Get text bounding box
    if font:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        text_width = len(text) * 6
        text_height = 20
    
    # Center the text
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # Draw the text
    draw.text((x, y), text, fill='#888888', font=font, align='center')
    
    # Draw a simple border
    draw.rectangle([0, 0, size[0]-1, size[1]-1], outline='#555555', width=2)
    
    # Save the image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, 'JPEG', quality=85)
    print(f"Created placeholder image: {output_path}")

if __name__ == "__main__":
    create_placeholder_image()