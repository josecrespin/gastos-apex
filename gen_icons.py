# Genera los íconos AS (Apex Sync) de ambas PWAs:
#   raíz  = Obras (azul)   ·   personal/ = Gastos José (verde)
import os
from PIL import Image, ImageDraw, ImageFont

FONDO = (12, 13, 16)
PALETAS = {
    '.':        ((79, 124, 255), (59, 95, 217)),   # azul obras
    'personal': ((47, 191, 113), (36, 154, 89)),   # verde personal
}

def degrade(size, c1, c2):
    img = Image.new('RGB', (size, size), FONDO)
    d = ImageDraw.Draw(img)
    for y in range(size):
        t = y / size
        c = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
        d.line([(0, y), (size, y)], fill=c)
    return img

def fuente(px):
    for ruta in ('/System/Library/Fonts/Helvetica.ttc',
                 '/System/Library/Fonts/Supplemental/Arial Bold.ttf'):
        try:
            return ImageFont.truetype(ruta, px, index=1)  # index 1 = bold en Helvetica.ttc
        except Exception:
            try:
                return ImageFont.truetype(ruta, px)
            except Exception:
                continue
    return ImageFont.load_default()

def icono(size, ruta, c1, c2):
    img = degrade(size, c1, c2)
    d = ImageDraw.Draw(img)
    f = fuente(int(size * 0.42))
    caja = d.textbbox((0, 0), 'AS', font=f)
    w, h = caja[2] - caja[0], caja[3] - caja[1]
    d.text(((size - w) / 2 - caja[0], (size - h) / 2 - caja[1]), 'AS', font=f, fill=(255, 255, 255))
    img.save(ruta, 'PNG')
    print(ruta, size)

for carpeta, (c1, c2) in PALETAS.items():
    os.makedirs(carpeta, exist_ok=True)
    for size in (180, 192, 512):
        icono(size, os.path.join(carpeta, f'icon-{size}.png'), c1, c2)
