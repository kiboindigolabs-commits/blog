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

# カラー定義（ブルー・シアン系）
BLUE      = (14, 116, 220)    # #0e74dc メインブルー
CYAN      = (6, 182, 212)     # #06b6d4 シアン
DARK_BLUE = (7, 35, 90)       # #07235a 濃いネイビー
WHITE     = (255, 255, 255)
LIGHT_C   = (186, 230, 253)   # #bae6fd 薄いシアン
BG_LIGHT  = (240, 249, 255)   # #f0f9ff 薄い水色背景


def draw_robot(draw: ImageDraw.Draw, ox: int, oy: int, size: int):
    """シンプルなロボットアイコンを描画（ブルー・シアン系）"""
    s = size / 32

    def r(x, y, w, h, radius=0, fill=BLUE):
        draw.rounded_rectangle(
            [ox + x * s, oy + y * s, ox + (x + w) * s, oy + (y + h) * s],
            radius=radius * s, fill=fill
        )

    def c(x, y, radius, fill=BLUE):
        draw.ellipse(
            [ox + (x - radius) * s, oy + (y - radius) * s,
             ox + (x + radius) * s, oy + (y + radius) * s],
            fill=fill
        )

    # Body（グラデーション風：上がシアン、下がブルー）
    r(2, 9, 28, 22, 6, BLUE)
    r(2, 9, 28, 10, 6, CYAN)

    # Antenna
    r(13, 2, 6, 9, 3, DARK_BLUE)
    c(16, 3, 3, LIGHT_C)

    # Eyes (white boxes)
    r(6, 17, 7, 6, 2, WHITE)
    r(19, 17, 7, 6, 2, WHITE)
    # Pupils（シアン）
    c(9.5, 20, 2, CYAN)
    c(22.5, 20, 2, CYAN)

    # Mouth（白）
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

    # 左サイドバー（ブルー→シアン グラデーション風）
    for y in range(H):
        ratio = y / H
        r = int(DARK_BLUE[0] * (1 - ratio) + BLUE[0] * ratio)
        g = int(DARK_BLUE[1] * (1 - ratio) + BLUE[1] * ratio)
        b = int(DARK_BLUE[2] * (1 - ratio) + BLUE[2] * ratio)
        draw.line([(0, y), (400, y)], fill=(r, g, b))

    # 右エリア（薄い水色）
    draw.rectangle([400, 0, W, H], fill=BG_LIGHT)

    # 装飾：右エリアに薄いシアンの丸
    draw.ellipse([900, -80, 1280, 300], fill=(224, 247, 253))
    draw.ellipse([350, 400, 700, 750], fill=(219, 243, 252))

    # ロボットアイコン（左サイドバー中央）
    robot_size = 180
    draw_robot(draw, 110, 225, robot_size)

    # サイト名テキスト（左）
    try:
        font_title  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 76)
        font_sub    = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 34)
        font_tag    = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
        font_catch  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    except Exception:
        font_title = font_sub = font_tag = font_catch = ImageFont.load_default()

    # メインタイトル（右エリア）
    draw.text((440, 160), "AI Tools Lab", font=font_title, fill=DARK_BLUE)

    # 区切り線
    draw.rectangle([440, 260, 1100, 265], fill=CYAN)

    # サブタイトル
    draw.text((444, 285), "AIツールの最新情報・使い方・", font=font_sub, fill=(30, 60, 120))
    draw.text((444, 328), "おすすめをわかりやすく紹介", font=font_sub, fill=(30, 60, 120))

    # キャッチコピー
    draw.text((444, 400), "初心者にもわかりやすく、すぐに使える情報をお届け", font=font_catch, fill=BLUE)

    # タグ
    tags = ["ChatGPT", "Claude", "Gemini", "Midjourney", "AI活用"]
    tx = 444
    for tag in tags:
        bbox = draw.textbbox((0, 0), tag, font=font_tag)
        tw = bbox[2] - bbox[0] + 24
        draw.rounded_rectangle([tx, 465, tx + tw, 500], radius=6, fill=CYAN)
        draw.text((tx + 12, 468), tag, font=font_tag, fill=WHITE)
        tx += tw + 10

    # 下部バー（ブルー）
    draw.rectangle([0, H - 10, W, H], fill=BLUE)
    draw.rectangle([0, H - 10, 400, H], fill=DARK_BLUE)

    img.save(path, "PNG")
    print(f"  作成: {path.name} ({W}x{H})")


if __name__ == "__main__":
    print("ブログ用画像を生成しています...")
    make_favicon(16,  STATIC / "favicon-16x16.png")
    make_favicon(32,  STATIC / "favicon-32x32.png")
    make_favicon(180, STATIC / "apple-touch-icon.png")
    make_og_image(STATIC / "images" / "og-default.png")
    print("完了！")
