"""Contact sheet of an issue's panels. Usage: python3 contact_sheet.py issue02 out.jpg"""
import glob, os, sys
from PIL import Image, ImageDraw, ImageFont
tag, out = sys.argv[1], sys.argv[2]
fs = sorted(glob.glob(f'art/{tag}/p*.png'), key=lambda f: (int(os.path.basename(f)[1:3]), int(os.path.basename(f)[4])))
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
cell = (330, 330); cols = 6; rows = -(-len(fs) // cols)
sheet = Image.new('RGB', (cols * (cell[0] + 10) + 10, rows * (cell[1] + 40) + 10), (244, 239, 230)); d = ImageDraw.Draw(sheet)
for i, fn in enumerate(fs):
    im = Image.open(fn).convert('RGB'); im.thumbnail(cell)
    x = 10 + (i % cols) * (cell[0] + 10); y = 10 + (i // cols) * (cell[1] + 40)
    b = os.path.basename(fn)[:-4]; d.text((x, y), f"p{int(b[1:3])}.{b[4]}", fill=(55, 38, 25), font=f)
    sheet.paste(im, (x, y + 30))
os.makedirs(os.path.dirname(out), exist_ok=True); sheet.save(out, quality=88); print(out, len(fs))
