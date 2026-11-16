"""Draw the purple Velqora mark for app bundles and the window."""
from pathlib import Path
from PIL import Image, ImageDraw

assets = Path('assets')
assets.mkdir(exist_ok=True)
image = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)
draw.rounded_rectangle((78, 78, 946, 946), radius=238, fill='#5142dc')
draw.polygon([(329, 224), (426, 224), (511, 498), (596, 224),
              (692, 224), (559, 605), (463, 605)], fill='white')
image.save(assets / 'icon.png')
image.save(assets / 'icon.icns', format='ICNS')
