import os
import sys
import logging
from PIL import Image, ImageChops
from concurrent.futures import ThreadPoolExecutor, as_completed

# **Logging Setup**
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def find_center_of_non_transparent_area(image: Image.Image) -> tuple:
    """Find center of non-transparent area."""
    bbox = image.getbbox()
    if bbox is None:
        return (image.width // 2, image.height // 2)  # Default center
    left, upper, right, lower = bbox
    return ((left + right) // 2, (upper + lower) // 2)

def calculate_zoom_with_margins(image: Image.Image, final_size: tuple, margins: tuple, apply_margins: bool) -> float:
    """Calculate zoom factor, but only apply if margins are enabled."""
    if not apply_margins:
        return 1.0  # **No Zoom when margins are disabled**

    bbox = image.getbbox()
    if bbox is None:
        return 1.0  # No object found, default zoom factor

    object_width = bbox[2] - bbox[0]
    object_height = bbox[3] - bbox[1]

    top_margin, bottom_margin, left_margin, right_margin = margins
    available_width = final_size[0] - (left_margin + right_margin)
    available_height = final_size[1] - (top_margin + bottom_margin)

    return min(available_width / object_width, available_height / object_height)

def scale_image(image: Image.Image, zoom_factor: float) -> Image.Image:
    """Scale image based on zoom factor."""
    if zoom_factor == 1.0:
        return image  # **No resizing if zoom factor is 1.0**
    new_width = int(image.width * zoom_factor)
    new_height = int(image.height * zoom_factor)
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

def center_image(image: Image.Image, final_size: tuple, margins: tuple, apply_margins: bool) -> tuple:
    """Center the image, apply margins only if enabled."""
    center_x, center_y = find_center_of_non_transparent_area(image)

    if apply_margins:
        top_margin, bottom_margin, left_margin, right_margin = margins
    else:
        top_margin, bottom_margin, left_margin, right_margin = 0, 0, 0, 0  # **No margins**

    dx = ((final_size[0] - left_margin - right_margin) // 2) - center_x + left_margin
    dy = ((final_size[1] - top_margin - bottom_margin) // 2) - center_y + top_margin

    logging.info(f"Image centered: Move by (dx={dx}, dy={dy}) pixels. {'Margins Applied' if apply_margins else 'No Margins'}")
    
    centered_img = Image.new("RGBA", final_size, (0, 0, 0, 0))
    centered_img.paste(image, (dx, dy), image)

    return centered_img, (dx, dy)

def process_background(background_image: Image.Image, dx: int, dy: int, final_size: tuple) -> Image.Image:
    """Apply blue background and align properly."""
    blue_canvas = Image.new("RGB", final_size, (0, 0, 255))  # Blue BG
    bg_rgb = background_image.convert("RGB")
    blue_canvas.paste(bg_rgb, (dx, dy))
    return ImageChops.multiply(blue_canvas, Image.new("RGB", final_size, (0, 0, 255)))  # Blend

def compose_final_image(processed_bg: Image.Image, centered_transparent: Image.Image) -> Image.Image:
    """Merge the processed background and transparent image."""
    return Image.alpha_composite(processed_bg.convert("RGBA"), centered_transparent)

def process_image_pair(input_folder: str, output_folder: str, bg_file: str, no_bg_file: str, margins: tuple, apply_margins: bool):
    """Process an image pair (background + transparent) with conditional margins."""
    os.makedirs(output_folder, exist_ok=True)
    try:
        img_with_bg = Image.open(os.path.join(input_folder, bg_file))
        img_no_bg = Image.open(os.path.join(input_folder, no_bg_file))

        original_size = img_no_bg.size
        zoom_factor = calculate_zoom_with_margins(img_no_bg, original_size, margins, apply_margins)

        img_with_bg_scaled = scale_image(img_with_bg, zoom_factor)
        img_no_bg_scaled = scale_image(img_no_bg, zoom_factor)

        centered_transparent, (dx, dy) = center_image(img_no_bg_scaled, original_size, margins, apply_margins)
        processed_bg = process_background(img_with_bg_scaled, dx, dy, original_size)
        final_image = compose_final_image(processed_bg, centered_transparent)

        # **Save Output Images**
        centered_transparent.save(os.path.join(output_folder, no_bg_file), "PNG")
        final_image.save(os.path.join(output_folder, bg_file), "PNG")

        logging.info(f"Processed: {bg_file} | {'Margins Applied' if apply_margins else 'No Margins'} | Zoom Factor: {zoom_factor} | dx={dx}, dy={dy}")

    except Exception as e:
        logging.error(f"Error processing images in {input_folder}: {e}")

def process_images_in_folders(input_root: str, output_root: str, margins: tuple, apply_margins: bool):
    """Process images in all subfolders, applying margins conditionally."""
    subfolders = [f for f in os.listdir(input_root) if os.path.isdir(os.path.join(input_root, f))]

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_tasks = []
        for subfolder in subfolders:
            input_folder = os.path.join(input_root, subfolder)
            output_folder = os.path.join(output_root, subfolder)
            os.makedirs(output_folder, exist_ok=True)
            logging.info(f"Processing folder: {input_folder}")

            all_files = os.listdir(input_folder)
            categories = ["R", "W", "Y"]

            for category in categories:
                bg_images = [f for f in all_files if f.startswith(f"{subfolder}-{category}-") and f.endswith(".png")]
                no_bg_images = [f for f in all_files if f.startswith(f"{subfolder}-{category}A-") and f.endswith(".png")]

                for bg_file in bg_images:
                    corresponding_no_bg = bg_file.replace(f"-{category}-", f"-{category}A-")
                    if corresponding_no_bg in no_bg_images:
                        future_tasks.append(executor.submit(
                            process_image_pair, input_folder, output_folder, bg_file, corresponding_no_bg, margins, apply_margins
                        ))

        for future in as_completed(future_tasks):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error in thread execution: {e}")
# **Main Execution (Command Line Arguments)**
if __name__ == "__main__":
    if len(sys.argv) != 9:
        print("Usage: python script.py <input_folder> <output_folder> <top_margin> <right_margin> <bottom_margin> <left_margin>  <apply_margins : 0 or 1> <max_threads>")
        sys.exit(1)

    # **Read Command Line Arguments**
    input_folder_path = sys.argv[1]
    output_folder_path = sys.argv[2]
    top_margin = int(sys.argv[3])
    bottom_margin = int(sys.argv[4])
    left_margin = int(sys.argv[5])
    right_margin = int(sys.argv[6])
    apply_margins = bool(int(sys.argv[7]))  # 1 = Apply Margins, 0 = No Margins
    max_threads = int(sys.argv[8])  

    # **Check if max_threads is valid**
    if max_threads < 1:  
        print("Error: Thread count must be at least 1!")
        sys.exit(1)  # **Exit only if invalid input**

    # **Margins Tuple**
    margins = (top_margin, bottom_margin, left_margin, right_margin)

    # **Process Images**
    process_images_in_folders(input_folder_path, output_folder_path, margins, apply_margins)



# import os
# import sys
# import logging
# from PIL import Image, ImageChops
# from concurrent.futures import ThreadPoolExecutor, as_completed

# # **Logging Setup**
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# def find_center_of_non_transparent_area(image: Image.Image) -> tuple:
#     """Find center of non-transparent area."""
#     bbox = image.getbbox()
#     if bbox is None:
#         return (image.width // 2, image.height // 2)  # Default center
#     left, upper, right, lower = bbox
#     return ((left + right) // 2, (upper + lower) // 2)

# def calculate_zoom_with_margins(image: Image.Image, final_size: tuple, margins: tuple, apply_margins: bool) -> float:
#     """Calculate zoom factor, but only apply if margins are enabled."""
#     if not apply_margins:
#         return 1.0  # **No Zoom when margins are disabled**

#     bbox = image.getbbox()
#     if bbox is None:
#         return 1.0  # No object found, default zoom factor

#     object_width = bbox[2] - bbox[0]
#     object_height = bbox[3] - bbox[1]

#     top_margin, bottom_margin, left_margin, right_margin = margins
#     available_width = final_size[0] - (left_margin + right_margin)
#     available_height = final_size[1] - (top_margin + bottom_margin)

#     return min(available_width / object_width, available_height / object_height)

# def scale_image(image: Image.Image, zoom_factor: float) -> Image.Image:
#     """Scale image based on zoom factor."""
#     if zoom_factor == 1.0:
#         return image  # **No resizing if zoom factor is 1.0**
#     new_width = int(image.width * zoom_factor)
#     new_height = int(image.height * zoom_factor)
#     return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

# def center_image(image: Image.Image, final_size: tuple, margins: tuple, apply_margins: bool) -> tuple:
#     """Center the image, apply margins only if enabled."""
#     center_x, center_y = find_center_of_non_transparent_area(image)

#     if apply_margins:
#         top_margin, bottom_margin, left_margin, right_margin = margins
#     else:
#         top_margin, bottom_margin, left_margin, right_margin = 0, 0, 0, 0  # **No margins**

#     dx = ((final_size[0] - left_margin - right_margin) // 2) - center_x + left_margin
#     dy = ((final_size[1] - top_margin - bottom_margin) // 2) - center_y + top_margin

#     logging.info(f"Image centered: Move by (dx={dx}, dy={dy}) pixels. {'Margins Applied' if apply_margins else 'No Margins'}")
    
#     centered_img = Image.new("RGBA", final_size, (0, 0, 0, 0))
#     centered_img.paste(image, (dx, dy), image)

#     return centered_img, (dx, dy)

# def process_background(background_image: Image.Image, dx: int, dy: int, final_size: tuple, bg_color: tuple) -> Image.Image:
#     """Apply user-specified background color and align properly."""
#     color_canvas = Image.new("RGB", final_size, bg_color)  # Custom BG
#     bg_rgb = background_image.convert("RGB")
#     color_canvas.paste(bg_rgb, (dx, dy))
#     return ImageChops.multiply(color_canvas, Image.new("RGB", final_size, bg_color))  # Blend
# def compose_final_image(processed_bg: Image.Image, centered_transparent: Image.Image) -> Image.Image:
#     """Merge the processed background and transparent image."""
#     return Image.alpha_composite(processed_bg.convert("RGBA"), centered_transparent)

# def process_image_pair(input_folder: str, output_folder: str, bg_file: str, no_bg_file: str, margins: tuple, apply_margins: bool, bg_color: tuple):
#     """Process an image pair (background + transparent) with conditional margins."""
#     os.makedirs(output_folder, exist_ok=True)
#     try:
#         img_with_bg = Image.open(os.path.join(input_folder, bg_file))
#         img_no_bg = Image.open(os.path.join(input_folder, no_bg_file))

#         original_size = img_no_bg.size
#         zoom_factor = calculate_zoom_with_margins(img_no_bg, original_size, margins, apply_margins)

#         img_with_bg_scaled = scale_image(img_with_bg, zoom_factor)
#         img_no_bg_scaled = scale_image(img_no_bg, zoom_factor)

#         centered_transparent, (dx, dy) = center_image(img_no_bg_scaled, original_size, margins, apply_margins)
#         processed_bg = process_background(img_with_bg_scaled, dx, dy, original_size, bg_color)
#         final_image = compose_final_image(processed_bg, centered_transparent)

#         # **Save Output Images**
#         centered_transparent.save(os.path.join(output_folder, no_bg_file), "PNG")
#         final_image.save(os.path.join(output_folder, bg_file), "PNG")

#         logging.info(f"Processed: {bg_file} | {'Margins Applied' if apply_margins else 'No Margins'} | Zoom Factor: {zoom_factor} | dx={dx}, dy={dy}")

#     except Exception as e:
#         logging.error(f"Error processing images in {input_folder}: {e}")

# def process_images_in_folders(input_root: str, output_root: str, margins: tuple, apply_margins: bool, bg_color: tuple):
#     """Process images in all subfolders, applying margins conditionally."""
#     subfolders = [f for f in os.listdir(input_root) if os.path.isdir(os.path.join(input_root, f))]

#     with ThreadPoolExecutor(max_workers=max_threads) as executor:
#         future_tasks = []
#         for subfolder in subfolders:
#             input_folder = os.path.join(input_root, subfolder)
#             output_folder = os.path.join(output_root, subfolder)
#             os.makedirs(output_folder, exist_ok=True)
#             logging.info(f"Processing folder: {input_folder}")

#             all_files = os.listdir(input_folder)
#             categories = ["R", "W", "Y"]

#             for category in categories:
#                 bg_images = [f for f in all_files if f.startswith(f"{subfolder}-{category}-") and f.endswith(".png")]
#                 no_bg_images = [f for f in all_files if f.startswith(f"{subfolder}-{category}A-") and f.endswith(".png")]

#                 for bg_file in bg_images:
#                     corresponding_no_bg = bg_file.replace(f"-{category}-", f"-{category}A-")
#                     if corresponding_no_bg in no_bg_images:
#                         future_tasks.append(executor.submit(
#                             process_image_pair, input_folder, output_folder, bg_file, corresponding_no_bg, margins, apply_margins, bg_color
#                         ))

#         for future in as_completed(future_tasks):
#             try:
#                 future.result()
#             except Exception as e:
#                 logging.error(f"Error in thread execution: {e}")

# if __name__ == "__main__":
#     input_folder_path = sys.argv[1]
#     output_folder_path = sys.argv[2]
#     margins = tuple(map(int, sys.argv[3:7]))
#     apply_margins = bool(int(sys.argv[7]))
#     max_threads = int(sys.argv[8])
#     bg_color = tuple(map(int, sys.argv[9].split(",")))  # RGB color from command line

#     process_images_in_folders(input_folder_path, output_folder_path, margins, apply_margins, bg_color)
