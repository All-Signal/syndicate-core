from PIL import Image, ImageDraw, ImageFont
import math

SIZE = 512
img = Image.new("RGBA", (SIZE, SIZE), color=(10, 10, 15, 255))
draw = ImageDraw.Draw(img)

# Draw subtle radial background glow
center_x, center_y = SIZE // 2, SIZE // 2
for r in range(250, 0, -5):
    alpha = int(45 * (1 - r / 250))
    draw.ellipse([center_x - r, center_y - r, center_x + r, center_y + r], outline=(155, 89, 182, alpha), width=3)

# Draw outer futuristic ring
draw.ellipse([40, 40, SIZE - 40, SIZE - 40], outline=(155, 89, 182, 220), width=4)

# Draw tech ticks / marks around ring
num_ticks = 36
for i in range(num_ticks):
    angle = (i * 360 / num_ticks) * math.pi / 180
    r1 = 200
    r2 = 210 if i % 3 == 0 else 205
    x1 = center_x + r1 * math.cos(angle)
    y1 = center_y + r1 * math.sin(angle)
    x2 = center_x + r2 * math.cos(angle)
    y2 = center_y + r2 * math.sin(angle)
    color = (26, 188, 156, 255) if i % 3 == 0 else (155, 89, 182, 160)
    draw.line([(x1, y1), (x2, y2)], fill=color, width=2)

# Inner hexagon
hex_r = 150
hex_points = []
for i in range(6):
    angle = (i * 60 - 30) * math.pi / 180
    x = center_x + hex_r * math.cos(angle)
    y = center_y + hex_r * math.sin(angle)
    hex_points.append((x, y))
draw.polygon(hex_points, outline=(26, 188, 156, 240), width=3)

# Draw bold stylized '1' or 'THE ONE' monolith in the center
# Central geometric glyph
draw.rectangle([center_x - 16, center_y - 80, center_x + 16, center_y + 80], fill=(255, 255, 255, 255))
# Top flag of the 1
draw.polygon([(center_x - 16, center_y - 80), (center_x - 50, center_y - 45), (center_x - 16, center_y - 45)], fill=(255, 255, 255, 255))
# Bottom pedestal
draw.rectangle([center_x - 50, center_y + 65, center_x + 50, center_y + 80], fill=(255, 255, 255, 255))

# Accents
draw.ellipse([center_x - 120, center_y - 120, center_x - 110, center_y - 110], fill=(241, 196, 15, 255))
draw.ellipse([center_x + 110, center_y + 110, center_x + 120, center_y + 120], fill=(241, 196, 15, 255))

img.save("/home/rudra/discord-server-setup/server_icon.png")
print("Saved /home/rudra/discord-server-setup/server_icon.png")
