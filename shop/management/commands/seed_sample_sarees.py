"""
Demo saree listings with photos downloaded from royalty-free stock (Unsplash).
Cannot embed Google Images (copyright / Terms of Use); Unsplash is licensed for this use.

Run: python manage.py seed_sample_sarees
"""

from decimal import Decimal
from io import BytesIO
import ssl
import urllib.request

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from shop.models import Category, Product, ProductImage

User = get_user_model()

CATEGORIES = [
    ("Silk", "silk"),
    ("Tissue Silk", "tissue-silk"),
    ("Jacquard", "jacquard"),
    ("Designer", "designer"),
    ("Banarasi", "banarasi"),
    ("Modal Silk", "modal-silk"),
    ("Brocade", "brocade"),
    ("Ready to Wear", "ready-to-wear"),
]

# Curated Unsplash fashion / textile photos (free license via unsplash.com/license)
STOCK_IMAGE_URLS = [
    "https://images.unsplash.com/photo-1594633313593-bab3825d0caf?w=800&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1583391739023-958efa920edb?w=800&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1562157873-818bc0726f8a?w=800&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1539008835657-9e8e9680c956?w=800&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=800&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=800&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1515377905703-c4788e51af15?w=800&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=800&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=800&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=800&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1617331721458-bd3bd3f9c7c8?w=800&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=800&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1509631179647-0177331693ae?w=800&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=800&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=800&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1445205170230-053b83016050?w=800&q=80&auto=format&fit=crop",
]

# (title, slug, category_slug, price, sale_price or None, colors, description)
SAMPLES = [
    (
        "Captivating Black Silk Embroidered Saree — Lajree",
        "captivating-black-silk-lajree",
        "silk",
        Decimal("3299"),
        Decimal("2499"),
        "Black, Gold",
        "Premium black silk with intricate zari-style embroidery. Boutique designer look.",
    ),
    (
        "Gulaabi Tissue Silk Saree — Manish Gharat",
        "gulaabi-tissue-silk-manish",
        "tissue-silk",
        Decimal("2899"),
        Decimal("2199"),
        "Hot Pink, Gold",
        "Vibrant tissue silk with a soft drape and festive shine.",
    ),
    (
        "Red Soft Silk Jacquard Saree — Whole Suits",
        "red-silk-jacquard-whole-suits",
        "jacquard",
        Decimal("3599"),
        Decimal("2799"),
        "Maroon, Gold",
        "Rich jacquard weave with traditional motifs across the body.",
    ),
    (
        "Dusty Blue Designer Silk — Rushini",
        "dusty-blue-designer-rushini",
        "designer",
        Decimal("4199"),
        Decimal("3199"),
        "Teal, Gold",
        "Statement designer piece with contrast border detail.",
    ),
    (
        "Thread Work Silk Saree — Andaaz Fashion",
        "thread-silk-andaaz",
        "silk",
        Decimal("2499"),
        Decimal("1999"),
        "Cyan, Silver",
        "Fine thread embroidery on lightweight silk for parties.",
    ),
    (
        "Beads Designer Saree — Cilory",
        "beads-designer-cilory",
        "designer",
        Decimal("2799"),
        Decimal("2299"),
        "Olive, Gold",
        "Subtle bead embellishments with a contemporary silhouette.",
    ),
    (
        "Black Floral Embroidered Saree — Little Wish",
        "black-floral-little-wish",
        "designer",
        Decimal("3099"),
        None,
        "Black, Multicolor",
        "Bold floral embroidery on deep black base.",
    ),
    (
        "Traditional Work Silk — Sareeka",
        "traditional-work-silk-sareeka",
        "silk",
        Decimal("4999"),
        Decimal("3999"),
        "Powder Blue, Silver",
        "Classic silk with all-over traditional woven patterns.",
    ),
    (
        "Yellow Silk Festive Saree — Zardozi Pune",
        "yellow-silk-zardozi-pune",
        "silk",
        Decimal("2699"),
        Decimal("2099"),
        "Yellow, Pink",
        "Bright festive yellow with contrast blouse tones.",
    ),
    (
        "Blue Embellished Silk — Soup by Sougat Paul",
        "blue-embellished-soup",
        "designer",
        Decimal("5499"),
        Decimal("4499"),
        "Teal, Gold",
        "High-contrast embellishment on deep teal silk.",
    ),
    (
        "1-Min Ready To Wear Saree — VIPNARI",
        "ready-to-wear-navy-vipnari",
        "ready-to-wear",
        Decimal("1899"),
        Decimal("1499"),
        "Navy, Gold",
        "Pre-draped friendly silhouette — quick festive styling.",
    ),
    (
        "Brocade Art Silk Saree — Swapna Weddings",
        "brocade-art-silk-swapna",
        "brocade",
        Decimal("3899"),
        Decimal("2999"),
        "Rose Pink, Gold",
        "Wedding-ready brocade with rich metallic highlights.",
    ),
    (
        "Diwali Banarasi Silk — I Love Sarees",
        "banarasi-magenta-diwali",
        "banarasi",
        Decimal("4599"),
        Decimal("3499"),
        "Magenta, Gold",
        "Vibrant Banarasi-inspired weave for celebrations.",
    ),
    (
        "Tempting Maroon Banarasi — Empress Clothing",
        "maroon-banarasi-empress",
        "banarasi",
        Decimal("5299"),
        Decimal("3999"),
        "Maroon, Gold",
        "Heavy traditional border with rich maroon body.",
    ),
    (
        "Modal Silk Plain Saree — Aham Designer",
        "modal-silk-plain-black-aham",
        "modal-silk",
        Decimal("1999"),
        Decimal("1599"),
        "Black, Gold",
        "Minimal modal silk — elegant for evening wear.",
    ),
    (
        "Pink Embroidered Saree — Saree Buta",
        "pink-embroidered-saree-buta",
        "designer",
        Decimal("2399"),
        Decimal("1899"),
        "Lilac, Silver",
        "Soft lilac-pink with delicate embroidery.",
    ),
    (
        "Pure Banarasi Border Silk — Sunasa",
        "pure-banarasi-border-sunasa",
        "banarasi",
        Decimal("5999"),
        Decimal("4799"),
        "Beige, Maroon, Gold",
        "Cream body with bold contrast border — timeless.",
    ),
    (
        "Red Silk Traditional — Karagiri",
        "red-silk-traditional-karagiri",
        "banarasi",
        Decimal("3499"),
        Decimal("2799"),
        "Red, Gold",
        "Classic red silk with woven border detail.",
    ),
]

FALLBACK_RGB = (220, 220, 230)


def _fetch_stock_image(url: str, filename_base: str) -> ContentFile | None:
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "SareeStoreSeed/1.0 (contact: store-admin; educational demo)",
                "Accept": "image/*",
            },
        )
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=45, context=ctx) as resp:
            data = resp.read()
            ct = resp.headers.get("Content-Type", "")
        if len(data) < 800:
            return None
        ext = "jpg"
        if "png" in ct.lower() or data[:8] == b"\x89PNG\r\n\x1a\n":
            ext = "png"
        elif "webp" in ct.lower() or data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            ext = "webp"
        safe = slugify(filename_base)[:50] or "img"
        return ContentFile(data, name=f"{safe}.{ext}")
    except Exception:
        return None


def _placeholder_image(name: str, rgb: tuple[int, int, int] = FALLBACK_RGB) -> ContentFile:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as e:
        raise RuntimeError("Pillow is required: pip install Pillow") from e

    w, h = 750, 1000
    img = Image.new("RGB", (w, h), rgb)
    draw = ImageDraw.Draw(img)
    r0, g0, b0 = rgb
    for y in range(h):
        t = y / h
        r = int(r0 + (255 - r0) * 0.15 * t)
        g = int(g0 + (255 - g0) * 0.12 * t)
        b = int(b0 + (255 - b0) * 0.12 * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    draw.rectangle([40, h // 2 - 80, w - 40, h // 2 + 120], outline=(255, 255, 255), width=3)
    try:
        font = ImageFont.truetype("arial.ttf", 28)
        font_small = ImageFont.truetype("arial.ttf", 20)
    except OSError:
        font = ImageFont.load_default()
        font_small = font

    title = "SareeMart Sample"
    words = name.split(" — ")[0]
    if len(words) > 42:
        words = words[:39] + "..."
    draw.text((50, h // 2 - 50), title, fill=(255, 255, 255), font=font)
    draw.text((50, h // 2 - 10), words, fill=(250, 250, 250), font=font_small)

    buf = BytesIO()
    img.save(buf, format="JPEG", quality=88)
    buf.seek(0)
    safe = slugify(name)[:40] or "saree"
    return ContentFile(buf.read(), name=f"{safe}.jpg")


class Command(BaseCommand):
    help = "Seed categories, sample_vendor, and 18 sarees with Unsplash stock images."

    def add_arguments(self, parser):
        parser.add_argument(
            "--vendor-password",
            default="demo123",
            help="Password for the sample_vendor account (default: demo123)",
        )

    def handle(self, *args, **options):
        pwd = options["vendor_password"]

        for name, slug in CATEGORIES:
            Category.objects.get_or_create(slug=slug, defaults={"name": name})

        vendor, _ = User.objects.get_or_create(
            username="sample_vendor",
            defaults={
                "email": "sample_vendor@example.com",
                "is_vendor": True,
            },
        )
        vendor.is_vendor = True
        vendor.set_password(pwd)
        vendor.save()

        created_n = 0
        updated_n = 0
        n_urls = len(STOCK_IMAGE_URLS)

        for idx, row in enumerate(SAMPLES):
            title, slug, cat_slug, price, sale, colors, desc = row
            cat = Category.objects.get(slug=cat_slug)
            product, was_created = Product.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": title,
                    "description": desc,
                    "price": price,
                    "discounted_price": sale,
                    "category": cat,
                    "vendor": vendor,
                    "stock_quantity": 25,
                    "colors": colors,
                    "sizes": "Free Size",
                },
            )
            if was_created:
                created_n += 1
            else:
                updated_n += 1

            product.images.all().delete()
            img_url = STOCK_IMAGE_URLS[idx % n_urls]
            cf = _fetch_stock_image(img_url, slug) or _placeholder_image(title)
            ProductImage.objects.create(
                product=product,
                image=cf,
                alt_text=title[:200],
                sort_order=0,
            )

        self.stdout.write(self.style.SUCCESS(
            f"Done. Products created: {created_n}, updated: {updated_n}."
        ))
        self.stdout.write(
            "Seller dashboard: sample_vendor / your password -> "
            "/accounts/vendor/login/ then /dashboard/"
        )
        self.stdout.write(
            "Admin (staff only): createsuperuser then open "
            "http://127.0.0.1:8000/accounts/login/?next=/manage/"
        )
