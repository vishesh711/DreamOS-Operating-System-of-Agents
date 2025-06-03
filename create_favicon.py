#!/usr/bin/env python3
# Generate a simple favicon for DreamOS
from PIL import Image, ImageDraw, ImageFont
import os

# Create a 32x32 image with a black background
img = Image.new('RGBA', (32, 32), color=(26, 26, 46, 255))
draw = ImageDraw.Draw(img)

# Draw a white "D" for DreamOS
draw.rectangle([4, 4, 28, 28], outline=(15, 52, 96, 255), width=2)
draw.ellipse([8, 8, 24, 24], fill=(0, 183, 255, 255))

# Save as ICO file
img.save('dreamos/web/static/img/favicon.ico', format='ICO', sizes=[(32, 32)])

print("Favicon created successfully!") 