import numpy as np
from PIL import Image, ImageFilter, ImageDraw

# ---------- grid setup ----------
GRID_W, GRID_H = 92, 54
CELL = 7
IMG_W, IMG_H = GRID_W * CELL, GRID_H * CELL

grid = np.zeros((GRID_H, GRID_W), dtype=np.uint8)
age = np.zeros((GRID_H, GRID_W), dtype=np.float32)

# Gosper Glider Gun coordinates (col, row)
gun = [
    (24,0),
    (22,1),(24,1),
    (12,2),(13,2),(20,2),(21,2),(34,2),(35,2),
    (11,3),(15,3),(20,3),(21,3),(34,3),(35,3),
    (0,4),(1,4),(10,4),(16,4),(20,4),(21,4),
    (0,5),(1,5),(10,5),(14,5),(16,5),(17,5),(22,5),(24,5),
    (10,6),(16,6),(24,6),
    (11,7),(15,7),
    (12,8),(13,8),
]
ox, oy = 3, 3
for cx, cy in gun:
    grid[oy + cy, ox + cx] = 1

# a second gun, mirrored, firing back the other way so the two glider
# streams cross paths and collide mid-canvas
gun2 = [(35 - cx, 8 - cy) for cx, cy in gun]
ox2, oy2 = GRID_W - 3 - 36, GRID_H - 3 - 9
for cx, cy in gun2:
    grid[oy2 + cy, ox2 + cx] = 1

def step(g):
    padded = np.pad(g, 1)
    neighbors = sum(
        padded[1 + dr: 1 + dr + GRID_H, 1 + dc: 1 + dc + GRID_W]
        for dr in (-1, 0, 1) for dc in (-1, 0, 1) if not (dr == 0 and dc == 0)
    )
    born = (g == 0) & (neighbors == 3)
    survive = (g == 1) & ((neighbors == 2) | (neighbors == 3))
    return (born | survive).astype(np.uint8)

# color ramp: newborn -> hot cyan/white, ages toward deep violet/blue
def age_color(a):
    a = np.clip(a / 26.0, 0, 1)
    r = 40 + a * 170
    g = 235 - a * 120
    b = 210 + a * 45
    return np.stack([r, g, b], axis=-1)

BG = np.array([6, 8, 16], dtype=np.float32)

brightness = np.zeros((GRID_H, GRID_W), dtype=np.float32)
DECAY = 0.95  # phosphor persistence — higher = longer comet tails

frames = []
N_STEPS = 260
CAPTURE_EVERY = 2  # simulate every step, but only render/save every 2nd

for i in range(N_STEPS):
    brightness = np.maximum(brightness * DECAY, grid.astype(np.float32))

    if i % CAPTURE_EVERY == 0:
        colors = age_color(age)
        canvas = BG[None, None, :] * (1 - brightness[..., None]) + colors * brightness[..., None]
        canvas = np.clip(canvas, 0, 255).astype(np.uint8)

        small = Image.fromarray(canvas, mode="RGB")
        big = small.resize((IMG_W, IMG_H), Image.NEAREST)

        # bloom / glow pass
        glow_src = small.resize((IMG_W, IMG_H), Image.BILINEAR)
        glow = glow_src.filter(ImageFilter.GaussianBlur(radius=5))
        big_arr = np.asarray(big).astype(np.float32)
        glow_arr = np.asarray(glow).astype(np.float32)
        screened = 255 - (255 - big_arr) * (255 - glow_arr * 0.55) / 255
        screened = np.clip(screened, 0, 255).astype(np.uint8)
        frame_img = Image.fromarray(screened, mode="RGB")
        frame_img = frame_img.quantize(colors=160, method=Image.MEDIANCUT, dither=Image.NONE)

        frames.append(frame_img)

    new_grid = step(grid)
    new_age = np.where(new_grid == 1, np.where(grid == 1, age + 1, 0), 0).astype(np.float32)
    grid, age = new_grid, new_age

# save as optimized gif
frames[0].save(
    "/home/claude/demo_full.gif",
    save_all=True,
    append_images=frames[1:],
    duration=95,
    loop=0,
    optimize=True,
)
print("frames:", len(frames), "size:", frames[0].size)
