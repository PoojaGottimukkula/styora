import requests
import os


def download_image(url, filename="product.jpg"):
    """
    Download a single image from URL and save to filename
    """
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        with open(filename, "wb") as f:
            f.write(r.content)
        return filename
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None


def download_multiple_images(image_urls):
    """
    Download multiple images and save them in images/ folder
    """
    os.makedirs("images", exist_ok=True)

    paths = []

    for i, url in enumerate(image_urls):
        filename = f"images/product_{i}.jpg"
        path = download_image(url, filename)
        if path:
            paths.append(path)

    return paths