#!/usr/bin/env python3
"""
ブログ用画像を生成するスクリプト
生成物:
  static/favicon-16x16.png
  static/favicon-32x32.png
  static/apple-touch-icon.png  (180x180)
  static/images/og-default.png (1200x630)
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

STATIC = Path(__file__).parent.parent / "static"
STATIC.mkdir(exist_ok=True)
(STATIC / "images").mkdir(exist_ok=True)

# カラー定義
INDIGO   = (99, 102, 241)    # #6366f1
VIOLET   = (139, 92, 246)    # #8b5cf6
WHITE    = (255, 255, 255)
LIGHT    = (199, 210, 254)   # #c7d2fe
BG_LIGHT = (238, 242, 255)   # 薄いインディゴ背景
DARK     = (30, 27, 75)      # #1e1b4b


def draw_robot(draw: ImageDraw.Draw, ox: int, oy: int, size: int):
    """シンプルなロボットアイコンを描画"""
    s = size / 32  # スケール係数

    def r(x, y, w, h, radius=0, fill=INDIGO):
        draw.rounded_rectangle(
            [ox + x * s, oy + y * s, ox + (x + w) * s, oy + (y + h) * s],
            radius=radius * s, fill=fill
        )

    def c(x, y, radius, fill=INDIGO):
        draw.ellipse(
            [ox + (x - radius) * s, oy + (y - radius) * s,
             ox + (x + radius) * s, oy + (y + radius) * s],
            fill=fill
        )

    # Body
    r(2, 9, 28, 22, 6, INDIGO)
    # Gradient overlay on body (lighter top)
    r(2, 9, 28, 11, 6, VIOLET)

    # Antenna
    r(13, 2, 6, 9, 3, INDIGO)
    c(16, 3, 3, LIGHT)

    # Eyes (white boxes)
    r(6, 17, 7, 6, 2, WHITE)
    r(19, 17, 7, 6, 2, WHITE)
    # Pupils
    c(9.5, 20, 2, INDIGO)
    c(22.5, 20, 2, INDIGO)

    # Mouth
    r(9, 27, 14, 3, 1.5, (255, 255, 255, 215))


def make_favicon(size: int, path: Path):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_robot(draw, 0, 0, size)
    img.save(path, "PNG")
    print(f"  作成: {path.name} ({size}x{size})")


def make_og_image(path: Path):
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), BG_LIGHT)
    draw = ImageDraw.Draw(img)

    # 背景グラデーション風の帯
    for y in range(H):
        ratio = y / H
        r = int(INDIGO[0] * (1 - ratio) + VIOLET[0] * ratio)
        g = int(INDIGO[1] * (1 - ratio) + VIOLET[1] * ratio)
        b = int(INDIGO[2] * (1 - ratio) + VIOLET[2] * ratio)
        draw.line([(0, y), (420, y)], fill=(r, g, b))

    # 右側は薄いインディゴ
    draw.rectangle([420, 0, W, H], fill=BG_LIGHT)

    # ロボットアイコン（左側白エリア）
    robot_size = 200
    draw_robot(draw, 110, 215, robot_size)

    # テキスト（右エリア）
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        font_sub   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        font_tag   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub   = font_title
        font_tag   = font_title

    # タイトル
    draw.text((460, 200), "AI Tools Lab", font=font_title, fill=DARK)
    # サブタイトル
    draw.text((462, 300), "AIツールの最新情報・使い方・", font=font_sub, fill=(80, 80, 120))
    draw.text((462, 345), "おすすめをわかりやすく紹介", font=font_sub, fill=(80, 80, 120))
    # タグライン
    draw.text((462, 430), "ChatGPT / Claude / Gemini / Midjourney", font=font_tag, fill=INDIGO)

    # 下部バー
    draw.rectangle([0, H - 8, W, H], fill=INDIGO)

    img.save(path, "PNG")
    print(f"  作成: {path.name} ({W}x{H})")


if __name__ == "__main__":
    print("ブログ用画像を生成しています...")
    make_favicon(16,  STATIC / "favicon-16x16.png")
    make_favicon(32,  STATIC / "favicon-32x32.png")
    make_favicon(180, STATIC / "apple-touch-icon.png")
    make_og_image(STATIC / "images" / "og-default.png")
    print("完了！")
