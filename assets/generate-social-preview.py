#!/usr/bin/env python3
"""Build the ground-my-ui social preview pair from the generated artwork.

The source artwork was generated with OpenAI's built-in image generation tool.
This script deterministically normalizes that artwork, applies the house fade,
and composites the exact approved copy. Fonts are macOS Avenir Next — on
other platforms install an equivalent or the script stops at FONT_PATHS.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ASSETS = Path(__file__).resolve().parent
ARTWORK = ASSETS / "social-preview-artwork.png"
BASE = ASSETS / "social-preview-base.png"
FINAL = ASSETS / "social-preview.png"

CREAM = (254, 245, 229)
INK = (16, 33, 43)
TEAL = (31, 143, 138)
CORAL = (226, 86, 74)

# The fade below is solid cream to x=560 and clear by x=850 in base space, with
# alpha = 255*(1-t)**2. Text stays where alpha is still >=90% of cream, i.e.
# t<=0.051 -> x<=575 in base space, scaled by 1200/1731 for the final canvas.
SAFE_RIGHT = round(575 * 1200 / 1731)

FONT_PATHS = (
    Path("/System/Library/Fonts/Avenir Next.ttc"),
    Path("/Library/Fonts/Avenir Next.ttc"),
)


def font(size: int, index: int) -> ImageFont.FreeTypeFont:
    for path in FONT_PATHS:
        if path.exists():
            return ImageFont.truetype(str(path), size, index=index)
    raise FileNotFoundError("Avenir Next is required to reproduce the text layer")


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_ratio = size[0] / size[1]
    source_ratio = image.width / image.height
    if source_ratio > target_ratio:
        crop_width = round(image.height * target_ratio)
        left = (image.width - crop_width) // 2
        image = image.crop((left, 0, left + crop_width, image.height))
    elif source_ratio < target_ratio:
        crop_height = round(image.width / target_ratio)
        top = (image.height - crop_height) // 2
        image = image.crop((0, top, image.width, top + crop_height))
    return image.resize(size, Image.Resampling.LANCZOS)


def add_house_fade(image: Image.Image, solid_until: int, clear_at: int) -> Image.Image:
    overlay = Image.new("RGBA", image.size, CREAM + (0,))
    alpha = Image.new("L", image.size)
    pixels = alpha.load()
    for x in range(image.width):
        if x <= solid_until:
            value = 255
        elif x >= clear_at:
            value = 0
        else:
            t = (x - solid_until) / (clear_at - solid_until)
            value = round(255 * (1 - t) ** 2)
        for y in range(image.height):
            pixels[x, y] = value
    overlay.putalpha(alpha)
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def build() -> None:
    artwork = Image.open(ARTWORK).convert("RGB")

    base = cover(artwork, (1731, 909))
    base = add_house_fade(base, solid_until=560, clear_at=850)
    base.save(BASE, optimize=True)

    final = cover(base, (1200, 630))
    draw = ImageDraw.Draw(final)
    x = 76

    # The name is set on two lines, as reproduce-my-bug sets "reproduce / my bug".
    # On one line it ran past SAFE_RIGHT into the illustration; siblings keep the
    # whole text block on flat cream.
    # TTC indices: 8 Heavy, 2 Demi Bold, 0 Bold.
    layout = (
        ((x, 156), "ground\nmy ui", font(69, 8), INK, 6),
        ((x, 324), "Verify the contracts.\nThen design.", font(29, 2), TEAL, 4),
        ((x, 424), "Nothing errored.\nThat is the problem.", font(21, 0), CORAL, 4),
    )
    for xy, text, f, fill, spacing in layout:
        draw.multiline_text(xy, text, font=f, fill=fill, spacing=spacing)

    # Verify by measurement, not assertion: every line must end left of the point
    # where the house fade is still effectively opaque cream.
    for xy, text, f, _fill, spacing in layout:
        right = draw.multiline_textbbox(xy, text, font=f, spacing=spacing)[2]
        label = text.replace("\n", " / ")
        print(f"  right={right:4d} (limit {SAFE_RIGHT})  {label}")
        if right > SAFE_RIGHT:
            raise AssertionError(f"text overruns the cream area: {label!r} ends at {right}")

    final.save(FINAL, optimize=True)


if __name__ == "__main__":
    build()
