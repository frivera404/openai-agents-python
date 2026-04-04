from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "favicon_32x32.png"
OUT = ROOT / "favicon.ico"


def make_favicon(src: Path, out: Path):
    if not src.exists():
        raise SystemExit(f"Source image not found: {src}")
    im = Image.open(src).convert("RGBA")
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
    icons = [im.resize(s, Image.LANCZOS) for s in sizes]
    icons[0].save(out, format="ICO", sizes=sizes)
    print("WROTE", out)


if __name__ == "__main__":
    make_favicon(SRC, OUT)
