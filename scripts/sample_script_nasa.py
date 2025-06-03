#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests", "matplotlib", "Pillow"]
# ///

import requests
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import os
import sys

# NASA APOD API endpoint and demo key
NASA_APOD_URL = "https://api.nasa.gov/planetary/apod"
API_KEY = "DEMO_KEY"  # Replace with your API key for higher rate limits


def fetch_apod_images(count=16):
    """
    Fetches a list of APOD image metadata from NASA's API.
    """
    try:
        response = requests.get(NASA_APOD_URL, params={"api_key": API_KEY, "count": count})
        response.raise_for_status()
        data = response.json()
        return [item for item in data if item.get("media_type") == "image"]
    except requests.RequestException as e:
        print(f"Error fetching images: {e}")
        sys.exit(1)


def display_images_in_grid(images):
    """
    Displays images in a 4x4 matplotlib grid and allows the user to select one for download.
    """
    fig, axes = plt.subplots(4, 4, figsize=(12, 12))
    fig.suptitle("Click on an image to download it", fontsize=16)
    fig.subplots_adjust(hspace=0.5)

    # Flatten axes for easy indexing
    axes = axes.flatten()
    image_objs = []

    for idx, (ax, image_data) in enumerate(zip(axes, images)):
        try:
            img_resp = requests.get(image_data["url"])
            img_resp.raise_for_status()
            img = Image.open(BytesIO(img_resp.content))
            ax.imshow(img)
            ax.set_title(f"{idx + 1}")
            ax.axis("off")
            image_objs.append((img, image_data))
        except Exception as e:
            ax.axis("off")
            ax.set_title("Error")
            print(f"Error loading image {idx + 1}: {e}")
            image_objs.append((None, image_data))

    def on_click(event):
        for idx, ax in enumerate(axes):
            if ax == event.inaxes and image_objs[idx][0]:
                img, meta = image_objs[idx]
                filename = meta["title"].replace(" ", "_").replace("/", "_") + ".jpg"
                img.save(filename)
                print(f"Image saved as '{filename}'")
                plt.close(fig)
                return

    fig.canvas.mpl_connect("button_press_event", on_click)
    plt.show()


if __name__ == "__main__":
    images = fetch_apod_images(16)
    display_images_in_grid(images)
