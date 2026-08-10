# Genera los íconos de ambas PWAs — marca Apex Sync "Deep Teal" v2:
# fondo degradé deep teal → abyss, vértice (triángulo trazo fino) + onda.
#   raíz      = Obras     (triángulo pearl + onda copper)
#   personal/ = Fin. José (triángulo copper + onda pearl)
import os, math
from PIL import Image, ImageDraw

DEEP   = (20, 49, 58)     # #14313A
ABYSS  = (15, 39, 46)     # #0F272E
PEARL  = (232, 226, 213)  # #E8E2D5
COPPER = (201, 143, 95)   # #C98F5F

S = 4  # supersampling para bordes suaves

def fondo(s):
    img = Image.new('RGB', (s, s), ABYSS)
    d = ImageDraw.Draw(img)
    for y in range(s):
        t = y / s
        c = tuple(int(DEEP[i] + (ABYSS[i] - DEEP[i]) * t) for i in range(3))
        d.line([(0, y), (s, y)], fill=c)
    return img

def triangulo(d, s, color, w):
    apex = (0.5 * s, 0.195 * s)
    bl = (0.235 * s, 0.72 * s)
    br = (0.765 * s, 0.72 * s)
    d.line([bl, apex, br, bl, apex], fill=color, width=w, joint='curve')

def onda(d, s, color, w):
    # Polígono relleno entre la curva desplazada ±w/2 por su normal
    # (una polilínea gruesa deja flecos en los joints de PIL).
    x0, x1 = 0.14 * s, 0.86 * s
    yc, a = 0.635 * s, 0.048 * s
    n = 160
    centro = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        ph = (x - x0) / (x1 - x0) * 2 * math.pi
        centro.append((x, yc + a * math.sin(ph)))
    arriba, abajo = [], []
    for i, (x, y) in enumerate(centro):
        j0, j1 = max(0, i - 1), min(n, i + 1)
        dx = centro[j1][0] - centro[j0][0]
        dy = centro[j1][1] - centro[j0][1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        arriba.append((x + nx * w / 2, y + ny * w / 2))
        abajo.append((x - nx * w / 2, y - ny * w / 2))
    d.polygon(arriba + abajo[::-1], fill=color)
    # puntas redondeadas
    for (x, y) in (centro[0], centro[-1]):
        d.ellipse([x - w/2, y - w/2, x + w/2, y + w/2], fill=color)

def icono(size, ruta, tri, wave):
    s = size * S
    img = fondo(s)
    d = ImageDraw.Draw(img)
    triangulo(d, s, tri, max(2, int(0.030 * s)))
    onda(d, s, wave, max(2, int(0.044 * s)))
    img = img.resize((size, size), Image.LANCZOS)
    img.save(ruta, 'PNG')
    print(ruta, size)

VARIANTES = {
    '.':        (PEARL, COPPER),
    'personal': (COPPER, PEARL),
}
for carpeta, (tri, wave) in VARIANTES.items():
    os.makedirs(carpeta, exist_ok=True)
    for size in (180, 192, 512):
        icono(size, os.path.join(carpeta, f'icon-{size}.png'), tri, wave)
