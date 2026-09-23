r"""
Insert Animated GIFs into PowerPoint presentation copy.
Target: C:\Users\ASUS\Desktop\mppt teqdimat - Copy.pptx
Slides:
- Slide 13: Shape 6 (Image 1) -> po_climbing_animation.gif
- Slide 16: Shape 5 (Image 0) -> partial_shading_animation.gif
All other shapes and slides remain 100% untouched.
"""

import os
import shutil
from pptx import Presentation

pptx_path = r"C:\Users\ASUS\Desktop\mppt teqdimat - Copy.pptx"
backup_path = r"C:\Users\ASUS\Desktop\mppt teqdimat - Copy.backup.pptx"

# 1. Create a safe backup first
shutil.copy2(pptx_path, backup_path)
print(f"Created safety backup at: {backup_path}")

prs = Presentation(pptx_path)

# Slide 13 (index 12)
s13 = prs.slides[12]
img1_s13 = None
for s in s13.shapes:
    if s.name == "Image 1":
        img1_s13 = s
        break

if img1_s13 is None:
    raise ValueError("Image 1 not found on Slide 13!")

s13_left = img1_s13.left
s13_top = img1_s13.top
s13_w = img1_s13.width
s13_h = img1_s13.height

# Remove old shape
sp13 = img1_s13._element
sp13.getparent().remove(sp13)

# Add animated GIF at exact same coordinates
gif13_path = os.path.abspath(r"experiments\results\formulas\po_climbing_animation.gif")
s13.shapes.add_picture(gif13_path, s13_left, s13_top, s13_w, s13_h)
print(f"Slide 13: Replaced Image 1 with {gif13_path}")

# Slide 16 (index 15)
s16 = prs.slides[15]
img0_s16 = None
for s in s16.shapes:
    if s.name == "Image 0":
        img0_s16 = s
        break

if img0_s16 is None:
    raise ValueError("Image 0 not found on Slide 16!")

s16_left = img0_s16.left
s16_top = img0_s16.top
s16_w = img0_s16.width
s16_h = img0_s16.height

# Remove old shape
sp16 = img0_s16._element
sp16.getparent().remove(sp16)

# Add animated GIF at exact same coordinates
gif16_path = os.path.abspath(r"experiments\results\formulas\partial_shading_animation.gif")
s16.shapes.add_picture(gif16_path, s16_left, s16_top, s16_w, s16_h)
print(f"Slide 16: Replaced Image 0 with {gif16_path}")

# Save back to target file
prs.save(pptx_path)
print(f"Successfully saved updated presentation to: {pptx_path}")

# Remove backup once confirmed
if os.path.exists(backup_path):
    os.remove(backup_path)
    print("Cleaned up temporary safety backup.")
