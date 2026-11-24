import math
import os
import time
from PIL import Image

IMAGE_PATH = "krathong.png"
CAPTION_TEXT = "ลอยกระทงกันอูนน่ะห์"
ASCII_CHARS = " .:-=+*#%@"


def build_color_grid(image_path: str, base_width: int = 54):
    img = Image.open(image_path).convert("RGBA")
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    img = Image.alpha_composite(bg, img).convert("RGB")

    orig_w, orig_h = img.size
    aspect_ratio = orig_h / orig_w
    base_height = max(10, int(base_width * aspect_ratio * 0.48))

    resized = img.resize((base_width, base_height), Image.Resampling.LANCZOS)
    pixels = resized.load()

    grid = []
    for y in range(base_height):
        row = []
        for x in range(base_width):
            r, g, b = pixels[x, y]
            if r > 242 and g > 242 and b > 242:
                row.append(None)
            else:
                brightness = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
                row.append((r, g, b, brightness))
        grid.append(row)

    return grid, base_width, base_height


def render_frame(grid, base_w: int, base_h: int, t: float):
    bounce = math.sin(t * 7.5)
    scale_y = 1.0 + 0.10 * bounce
    scale_x = 1.0 / math.sqrt(scale_y)
    sway_x = int(3 * math.sin(t * 3.8))
    caption_bob = int(1.2 * math.sin(t * 5.0))

    out_w = max(10, int(round(base_w * scale_x)))
    out_h = max(8, int(round(base_h * scale_y)))

    lines = ["\033[H"]

    for oy in range(out_h):
        sy = min(base_h - 1, int(oy / scale_y))
        row_chars = [" " * max(0, 6 + sway_x)]

        for ox in range(out_w):
            sx = min(base_w - 1, int(ox / scale_x))
            cell = grid[sy][sx]

            if cell is None:
                row_chars.append(" ")
            else:
                r, g, b, brightness = cell
                idx = min(len(ASCII_CHARS) - 1, int((1.0 - brightness) * len(ASCII_CHARS)))
                ch = ASCII_CHARS[idx]
                row_chars.append(f"\033[38;2;{r};{g};{b}m{ch}")

        row_chars.append("\033[0m")
        lines.append("".join(row_chars))

    # เพิ่มบรรทัดว่างและข้อความด้านล่าง
    lines.append("")
    if caption_bob < 0:
        lines.append("")

    # เปลี่ยนสีข้อความโทนอบอุ่นทอง-ชมพูตามเวลา
    r_txt = int(235 + 20 * math.sin(t * 4.0))
    g_txt = int(195 + 45 * math.sin(t * 4.0 + 1.0))
    b_txt = int(120 + 60 * math.sin(t * 4.0 + 2.0))

    text_indent = " " * max(0, 12 + sway_x)
    lines.append(f"{text_indent}\033[1;38;2;{r_txt};{g_txt};{b_txt}m~*~ {CAPTION_TEXT} ~*~\033[0m")

    # เติมช่องว่างด้านล่างเพื่อไม่ให้ข้อความเก่าค้างเวลาขยับขึ้น-ลง
    lines.append(" " * 60)
    lines.append(" " * 60)

    print("\n".join(lines), flush=True)


def main():
    if not os.path.exists(IMAGE_PATH):
        print(f"ไม่พบไฟล์รูปภาพ: {IMAGE_PATH}")
        return

    grid, base_w, base_h = build_color_grid(IMAGE_PATH, base_width=54)

    os.system("cls" if os.name == "nt" else "clear")
    print("\033[?25l", end="", flush=True)

    fps = 24
    dt = 1.0 / fps
    t = 0.0

    try:
        while True:
            start = time.perf_counter()
            render_frame(grid, base_w, base_h, t)
            elapsed = time.perf_counter() - start
            time.sleep(max(0.0, dt - elapsed))
            t += dt
    except KeyboardInterrupt:
        print("\033[0m\033[?25h")
        print("หยุดแอนิเมชันเรียบร้อยแล้วครับ")


if __name__ == "__main__":
    main()