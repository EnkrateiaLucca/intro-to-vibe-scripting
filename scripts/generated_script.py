#!/usr/bin/env python3
"""
NASA Image Viewer and Selector

This script fetches 8 random images from NASA's API, displays them in a grid,
and allows you to select one to save locally using matplotlib's interactive features.

Usage:
    uv run nasa_image_selector.py

Controls:
    - Click on any image to select and save it
    - Close the window to exit without saving

Requirements:
    - Internet connection
    - NASA API access (no key required for this endpoint)
"""

# /// script
# dependencies = [
#     "requests>=2.31.0",
#     "matplotlib>=3.7.0",
#     "pillow>=10.0.0",
# ]
# ///

import requests
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
import io
import os
import sys
from datetime import datetime, timedelta
import random
from typing import List, Dict, Optional
import tempfile


class NASAImageFetcher:
    """Handles fetching images from NASA's API."""
    
    def __init__(self):
        self.base_url = "https://api.nasa.gov/planetary/apod"
        self.api_key = "DEMO_KEY"  # NASA provides a demo key for testing
        
    def fetch_random_images(self, count: int = 8) -> List[Dict]:
        """
        Fetch random images from NASA's Astronomy Picture of the Day API.
        
        Args:
            count: Number of images to fetch
            
        Returns:
            List of image data dictionaries
        """
        images = []
        print(f"🚀 Fetching {count} images from NASA API...")
        
        # Generate random dates from the past 2 years
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)
        
        for i in range(count):
            try:
                # Generate random date
                random_days = random.randint(0, 730)
                random_date = start_date + timedelta(days=random_days)
                date_str = random_date.strftime("%Y-%m-%d")
                
                print(f"  📡 Fetching image {i+1}/{count} for date {date_str}...")
                
                params = {
                    'api_key': self.api_key,
                    'date': date_str
                }
                
                response = requests.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                # Only include if it's an image (not a video)
                if data.get('media_type') == 'image' and 'url' in data:
                    images.append({
                        'title': data.get('title', 'Unknown'),
                        'url': data['url'],
                        'date': data.get('date', date_str),
                        'explanation': data.get('explanation', ''),
                        'hdurl': data.get('hdurl', data['url'])  # High-res version if available
                    })
                    print(f"    ✅ Got: {data.get('title', 'Unknown')}")
                else:
                    print(f"    ⏭️  Skipping non-image content")
                    
            except requests.RequestException as e:
                print(f"    ❌ Error fetching image {i+1}: {e}")
                continue
            except Exception as e:
                print(f"    ❌ Unexpected error for image {i+1}: {e}")
                continue
        
        if len(images) < count:
            print(f"⚠️  Only found {len(images)} images out of {count} requested")
            
        return images


class ImageGridViewer:
    """Handles displaying images in a grid and managing user selection."""
    
    def __init__(self, images: List[Dict]):
        self.images = images
        self.selected_image = None
        self.fig = None
        self.axes = None
        self.image_objects = []
        
    def download_and_display_images(self) -> bool:
        """
        Download images and display them in a grid.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.images:
            print("❌ No images to display")
            return False
            
        print(f"🖼️  Downloading and preparing {len(self.images)} images for display...")
        
        # Calculate grid dimensions
        n_images = len(self.images)
        cols = min(4, n_images)
        rows = (n_images + cols - 1) // cols
        
        # Create figure and subplots
        self.fig, self.axes = plt.subplots(rows, cols, figsize=(16, 12))
        self.fig.suptitle('NASA Images - Click on an image to select and save it', 
                         fontsize=16, fontweight='bold')
        
        # Handle case where we have only one row
        if rows == 1:
            self.axes = [self.axes] if n_images == 1 else self.axes
        else:
            self.axes = self.axes.flatten()
        
        # Download and display each image
        for i, img_data in enumerate(self.images):
            try:
                print(f"  📥 Downloading image {i+1}/{n_images}: {img_data['title'][:50]}...")
                
                # Download image
                response = requests.get(img_data['url'], timeout=15)
                response.raise_for_status()
                
                # Open image with PIL
                image = Image.open(io.BytesIO(response.content))
                
                # Display image
                ax = self.axes[i]
                ax.imshow(image)
                ax.set_title(f"{i+1}. {img_data['title'][:30]}...", 
                           fontsize=10, pad=10)
                ax.axis('off')
                
                # Store image data for saving later
                self.image_objects.append({
                    'data': response.content,
                    'info': img_data,
                    'index': i
                })
                
                print(f"    ✅ Displayed successfully")
                
            except Exception as e:
                print(f"    ❌ Error loading image {i+1}: {e}")
                # Show placeholder
                ax = self.axes[i]
                ax.text(0.5, 0.5, f'Error loading\n{img_data["title"][:20]}...', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_title(f"{i+1}. Error", fontsize=10, pad=10)
                ax.axis('off')
        
        # Hide unused subplots
        for i in range(len(self.images), len(self.axes)):
            self.axes[i].axis('off')
        
        # Connect click event
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        plt.tight_layout()
        return True
    
    def on_click(self, event):
        """Handle mouse click events on the images."""
        if event.inaxes is None:
            return
            
        # Find which subplot was clicked
        for i, ax in enumerate(self.axes):
            if ax == event.inaxes and i < len(self.image_objects):
                self.selected_image = self.image_objects[i]
                print(f"\n🎯 Selected image {i+1}: {self.selected_image['info']['title']}")
                
                # Highlight selected image
                for j, axis in enumerate(self.axes):
                    if j < len(self.images):
                        if j == i:
                            # Highlight selected
                            axis.set_title(f"✅ {j+1}. {self.images[j]['title'][:30]}...", 
                                         fontsize=10, pad=10, color='green', fontweight='bold')
                        else:
                            # Reset others
                            axis.set_title(f"{j+1}. {self.images[j]['title'][:30]}...", 
                                         fontsize=10, pad=10, color='black', fontweight='normal')
                
                plt.draw()
                
                # Save the image
                self.save_selected_image()
                break
    
    def save_selected_image(self):
        """Save the selected image to local disk."""
        if not self.selected_image:
            return
            
        try:
            img_info = self.selected_image['info']
            
            # Create filename
            safe_title = "".join(c for c in img_info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
            
            # Get file extension from URL
            url = img_info['url']
            extension = '.jpg'  # Default
            if '.' in url.split('/')[-1]:
                extension = '.' + url.split('.')[-1].split('?')[0]
            
            filename = f"nasa_{img_info['date']}_{safe_title}{extension}"
            
            # Save image
            with open(filename, 'wb') as f:
                f.write(self.selected_image['data'])
            
            print(f"💾 Image saved as: {filename}")
            print(f"📅 Date: {img_info['date']}")
            print(f"📝 Title: {img_info['title']}")
            print(f"🔗 Original URL: {img_info['url']}")
            
            if img_info.get('explanation'):
                print(f"📖 Description: {img_info['explanation'][:200]}...")
            
            print(f"\n✨ Image successfully saved! You can close the window now.")
            
        except Exception as e:
            print(f"❌ Error saving image: {e}")
    
    def show(self):
        """Display the image grid."""
        if self.fig:
            print(f"\n🖼️  Displaying image grid. Click on any image to select and save it.")
            print("   Close the window when you're done.")
            plt.show()


def main():
    """Main function to run the NASA image selector."""
    print("🌟 NASA Image Selector")
    print("=" * 50)
    
    try:
        # Fetch images from NASA API
        fetcher = NASAImageFetcher()
        images = fetcher.fetch_random_images(8)
        
        if not images:
            print("❌ No images could be fetched. Please check your internet connection and try again.")
            sys.exit(1)
        
        print(f"\n✅ Successfully fetched {len(images)} images!")
        
        # Display images in grid
        viewer = ImageGridViewer(images)
        
        if viewer.download_and_display_images():
            viewer.show()
        else:
            print("❌ Failed to display images.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()