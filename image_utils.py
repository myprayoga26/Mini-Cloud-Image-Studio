import io
from PIL import Image, ImageEnhance, ImageFilter


def resize_image(image, width, height):
    """Resize gambar ke dimensi yang diberikan."""
    return image.resize(
        (int(width), int(height)),
        Image.Resampling.LANCZOS,
    )


def grayscale_image(image):
    """Mengubah gambar menjadi grayscale/hitam-putih."""
    return image.convert("L")


def blur_image(image, radius=4):
    """Memberikan efek blur sederhana."""
    return image.filter(ImageFilter.GaussianBlur(radius=float(radius)))


def high_contrast_image(image, factor=1.6):
    """Meningkatkan kontras gambar."""
    return ImageEnhance.Contrast(
        image.convert("RGB")
    ).enhance(float(factor))


def image_to_bytes(image, output_format="PNG"):
    """Mengubah objek PIL Image menjadi bytes."""
    buffer = io.BytesIO()

    # JPEG/JPG tidak mendukung RGBA/L, jadi ubah ke RGB.
    if output_format.upper() in {"JPEG", "JPG"} and image.mode != "RGB":
        image = image.convert("RGB")

    image.save(buffer, format=output_format)
    buffer.seek(0)
    return buffer.getvalue()