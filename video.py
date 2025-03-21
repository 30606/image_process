# import os
# import cv2
# import pillow_avif
# import argparse
# from PIL import Image
# import concurrent.futures  # For multithreading

# # CLI argument parsing
# parser = argparse.ArgumentParser(description="Resize images and create a video.")
# parser.add_argument("-i", "--input-path", required=True, help="Path to the folder containing images")
# parser.add_argument("-o", "--output-path", required=True, help="Path to save the generated video")
# parser.add_argument("-t", "--threads", type=int, required=True, help="Number of threads for processing")
# parser.add_argument("-r", "--resolution", choices=["720p", "1080p", "4k", "8k"], required=True, help="Video resolution")
# parser.add_argument("-f", "--format", choices=["jpg", "png", "webp", "avif"], required=True, help="Output image format")

# # Add optional format-specific parameters
# parser.add_argument("-q", "--quality", type=int, help="Quality (JPG, WEBP, AVIF only)")
# parser.add_argument("-s", "--speed", type=int, choices=range(0, 11), help="Encoding speed (AVIF only)")
# parser.add_argument("-c", "--compression", type=int, choices=range(0, 10), help="Compression level (PNG only)")

# args = parser.parse_args()

# # Resolution mapping
# resolution_map = {
#     "720p": (1280, 720),
#     "1080p": (1920, 1080),
#     "4k": (3840, 2160),
#     "8k": (7680, 4320)
# }
# width, height = resolution_map[args.resolution]
# output_format = args.format

# print(f"Selected Resolution: {width}x{height}, Format: {output_format}")

# # Path variables
# input_path = args.input_path
# output_path = args.output_path
# threads = args.threads

# # Format-specific parameters
# if output_format in ["jpg", "webp", "avif"]:
#     quality = args.quality if args.quality else 95  # Default quality
# else:
#     quality = None

# if output_format == "avif":
#     speed = args.speed if args.speed else 5  # Default AVIF encoding speed
# else:
#     speed = None

# if output_format == "png":
#     compression = args.compression if args.compression else 6  # Default PNG compression level
# else:
#     compression = None

# # Image extensions (JPEG, PNG, AVIF, WEBP support)
# valid_extensions = (".jpg", ".jpeg", ".png", ".avif", ".webp")

# # Image list fetch karva
# image_files = [file for file in os.listdir(input_path) if file.lower().endswith(valid_extensions)]
# num_of_images = len(image_files)

# if num_of_images == 0:
#     print("No images found in the directory!")
#     exit()

# print("Number of Images:", num_of_images)

# # Multithreading for resizing images
# processed_images = []

# def resize_image(file):
#     im = Image.open(os.path.join(input_path, file))
#     im_resized = im.resize((width, height), Image.LANCZOS)
    
#     # Convert & save in user-defined format
#     output_file = os.path.join(input_path, os.path.splitext(file)[0] + f".{output_format}")
    
#     if output_format == "jpg":
#         im_resized.save(output_file, "JPEG", quality=quality)
#     elif output_format == "png":
#         im_resized.save(output_file, "PNG", compress_level=compression)
#     elif output_format == "webp":
#         im_resized.save(output_file, "WEBP", quality=quality)
#     elif output_format == "avif":
#         im_resized.save(output_file, "AVIF", quality=quality, speed=speed)

#     processed_images.append(output_file)
#     print(f"{file} resized and saved as {output_format}")

# with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
#     executor.map(resize_image, image_files)

# # Function to generate video
# def generate_video():
#     video_name = os.path.join(output_path, f'output_video.mp4')

#     frame = cv2.imread(processed_images[0])
#     height, width, layers = frame.shape

#     # Codec selection
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     video = cv2.VideoWriter(video_name, fourcc, 30, (width, height))

#     for img_path in processed_images:
#         img = cv2.imread(img_path)
#         video.write(img)

#     video.release()
#     cv2.destroyAllWindows()
#     print(f"Video generated successfully: {video_name}")

# # Generate video
# generate_video()


import cv2
print(cv2.__version__)