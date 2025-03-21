import os
import logging
from PIL import Image, ImageChops
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def find_center_of_non_transparent_area(image: Image.Image) -> tuple:
    """Find center of non-transparent area in an image."""
    bbox = image.getbbox()
    if bbox is None:
        logging.warning("No non-transparent pixels found. Using the image center as fallback.")
        width, height = image.size
        return (width // 2, height // 2)
    left, upper, right, lower = bbox
    return ((left + right) // 2, (upper + lower) // 2)

def center_image(image: Image.Image, final_size) -> tuple:
    """Center the transparent image in a fixed canvas size."""
    center_x, center_y = find_center_of_non_transparent_area(image)
    dx = (final_size[0] // 2) - center_x
    dy = (final_size[1] // 2) - center_y
    logging.info(f"Image centered: Move by (dx={dx}, dy={dy}) pixels.")

    centered_img = Image.new("RGBA", final_size, (0, 0, 0, 0))
    centered_img.paste(image, (dx, dy), image)
    return centered_img, (dx, dy)

def process_background(background_image: Image.Image, dx: int, dy: int, final_size) -> Image.Image:
    """Process background image by adjusting its position."""
    blue_canvas = Image.new("RGB", final_size, (0, 0, 255))
    bg_rgb = background_image.convert("RGB")
    blue_canvas.paste(bg_rgb, (dx, dy))
    return ImageChops.multiply(blue_canvas, Image.new("RGB", final_size, (0, 0, 255)))

def compose_final_image(processed_bg: Image.Image, centered_transparent: Image.Image) -> Image.Image:
    """Combine the processed background with the transparent image."""
    return Image.alpha_composite(processed_bg.convert("RGBA"), centered_transparent)

def process_image_pair(input_folder: str, output_folder: str, bg_file: str, no_bg_file: str):
    """Process an image pair (background + transparent) and save results."""
    os.makedirs(output_folder, exist_ok=True)
    try:
        img_with_bg = Image.open(os.path.join(input_folder, bg_file))
        img_no_bg = Image.open(os.path.join(input_folder, no_bg_file))

        # Get actual image size (assuming both images have the same size)
        final_size = img_with_bg.size  

        centered_transparent, (dx, dy) = center_image(img_no_bg, final_size=final_size)
        processed_bg = process_background(img_with_bg, dx, dy, final_size=final_size)
        final_image = compose_final_image(processed_bg, centered_transparent)

        # Save output images
        centered_transparent.save(os.path.join(output_folder, no_bg_file), "PNG")
        final_image.save(os.path.join(output_folder, bg_file), "PNG")

        logging.info(f"Processed: {bg_file} | dx={dx}, dy={dy} | Size: {final_size}")

    except Exception as e:
        logging.error(f"Error processing images in {input_folder}: {e}")

def process_images_in_folders(input_root: str, output_root: str):
    """Process all images inside multiple subfolders and nested subfolders in parallel."""
    for root, dirs, _ in os.walk(input_root):
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_tasks = []
            for subfolder in dirs:
                # Process all subfolders without specific name conditions
                input_folder = os.path.join(root, subfolder)
                output_folder = os.path.join(output_root, os.path.relpath(input_folder, input_root))
                os.makedirs(output_folder, exist_ok=True)
                logging.info(f"Processing folder: {input_folder}")

                # Get all PNG images from folder
                all_files = os.listdir(input_folder)

                # Categories: R, W, Y
                categories = ["R", "W", "Y"]
                for category in categories:
                    bg_images = [f for f in all_files if f.startswith(f"{subfolder}-{category}-") and f.endswith(".png")]
                    no_bg_images = [f for f in all_files if f.startswith(f"{subfolder}-{category}A-") and f.endswith(".png")]

                    for bg_file in bg_images:
                        corresponding_no_bg = bg_file.replace(f"-{category}-", f"-{category}A-")
                        if corresponding_no_bg in no_bg_images:
                            future_tasks.append(executor.submit(
                                process_image_pair, input_folder, output_folder, bg_file, corresponding_no_bg
                            ))

            # Wait for all tasks to complete
            for future in as_completed(future_tasks):
                try:
                    future.result()
                except Exception as e:
                    logging.error(f"Error in thread execution: {e}")

if __name__ == "__main__":
    input_folder_path = r"C:\\Users\\UMANG VACHHANI\\Desktop\\image_process\\parents\\input"
    output_folder_path = r"C:\\Users\\UMANG VACHHANI\\Desktop\\image_process\\P_output"

    process_images_in_folders(input_folder_path, output_folder_path)


