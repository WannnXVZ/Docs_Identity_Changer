"""Generates a professional application icon for Word Identity Changer."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def create_app_icon(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    images = []

    for width, height in sizes:
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Background rounded rect (Royal Blue)
        margin = int(width * 0.08)
        radius = int(width * 0.22)
        draw.rounded_rectangle(
            [margin, margin, width - margin, height - margin],
            radius=radius,
            fill=(37, 99, 235, 255),  # #2563eb
            outline=(29, 78, 216, 255),
            width=max(1, int(width * 0.02)),
        )

        # Inner document page (White)
        doc_left = int(width * 0.28)
        doc_top = int(height * 0.22)
        doc_right = int(width * 0.76)
        doc_bottom = int(height * 0.78)
        draw.rounded_rectangle(
            [doc_left, doc_top, doc_right, doc_bottom],
            radius=int(width * 0.05),
            fill=(255, 255, 255, 255),
        )

        # "W" letter mark on document (Blue)
        # Draw 3 document text lines
        line_left = doc_left + int(width * 0.08)
        line_right = doc_right - int(width * 0.08)
        line_h = max(2, int(height * 0.04))

        y1 = doc_top + int(height * 0.14)
        y2 = doc_top + int(height * 0.24)
        y3 = doc_top + int(height * 0.34)

        draw.rectangle([line_left, y1, line_right, y1 + line_h], fill=(37, 99, 235, 255))
        draw.rectangle([line_left, y2, line_right - int(width * 0.1), y2 + line_h], fill=(148, 163, 184, 255))
        draw.rectangle([line_left, y3, line_right - int(width * 0.05), y3 + line_h], fill=(148, 163, 184, 255))

        # ID Badge in bottom-left corner (Green)
        badge_r = int(width * 0.16)
        bx = int(width * 0.32)
        by = int(height * 0.68)
        draw.ellipse(
            [bx - badge_r, by - badge_r, bx + badge_r, by + badge_r],
            fill=(22, 163, 74, 255),  # #16a34a
            outline=(255, 255, 255, 255),
            width=max(1, int(width * 0.03)),
        )

        images.append(img)

    # Save as .ico containing all standard sizes
    images[0].save(
        output_path,
        format="ICO",
        sizes=[(s[0], s[1]) for s in sizes],
        append_images=images[1:],
    )
    print(f"Generated multi-resolution icon at {output_path}")


if __name__ == "__main__":
    icon_dest = Path(__file__).parent / "icon.ico"
    create_app_icon(icon_dest)
