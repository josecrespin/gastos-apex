# Genera los íconos AS (Apex Sync) de la PWA de gastos.
from PIL import Image, ImageDraw, ImageFont

AZUL = (79, 124, 255)
AZUL2 = (59, 95, 217)
FONDO = (12, 13, 16)

def degrade(size):
    img = Image.new('RGB', (size, size), FONDO)
    d = ImageDraw.Draw(img)
    for y in range(size):
        t = y / size
        c = tuple(int(AZUL[i] + (AZUL2[i] - AZUL[i]) * t) for i in range(3))
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

def icono(size, nombre):
    img = degrade(size)
    d = ImageDraw.Draw(img)
    f = fuente(int(size * 0.42))
    caja = d.textbbox((0, 0), 'AS', font=f)
    w, h = caja[2] - caja[0], caja[3] - caja[1]
    d.text(((size - w) / 2 - caja[0], (size - h) / 2 - caja[1]), 'AS', font=f, fill=(255, 255, 255))
    img.save(nombre, 'PNG')
    print(nombre, size)

icono(180, 'icon-180.png')
icono(192, 'icon-192.png')
icono(512, 'icon-512.png')
