# # import os
# # import argparse
# # import cv2
# # import numpy as np

# # # Argument Parser Setup
# # parser = argparse.ArgumentParser(description="Generate Video with Logo Overlay and Watermark")
# # parser.add_argument("-i", "--input", required=True, help="Input folder path")
# # parser.add_argument("-o", "--output", required=True, help="Output folder path")
# # parser.add_argument("-f", "--format", required=True, choices=["mp4", "mov"], help="Video format")
# # parser.add_argument("--fps", type=int, default=30, help="Frames per second (default: 30)")
# # parser.add_argument("-imgf", "--image_format", required=True, choices=["jpg", "jpeg", "png", "webp"], help="Input image format")
# # parser.add_argument("-l", "--logo", required=True, help="Company logo (PNG)")
# # parser.add_argument("-res", "--resolution", help="Custom resolution in WxH format (e.g., 1920x1080)")
# # parser.add_argument("-p", "--position", required=True, choices=["top-left", "top-right", "bottom-left", "bottom-right"], help="Logo position in video")
# # parser.add_argument("-wt", "--watermark_text", help="Watermark text to overlay on the video")
# # parser.add_argument("-wtf", "--watermark_font", required=True, choices=["SIMPLEX", "PLAIN", "DUPLEX", "COMPLEX", "TRIPLEX", "ITALIC"], help="Watermark text font type")

# # args = parser.parse_args()

# # # Ensure Output Folder Exists
# # output_folder = args.output
# # os.makedirs(output_folder, exist_ok=True)

# # # Construct Output Video Path
# # input_folder_name = os.path.basename(os.path.normpath(args.input))
# # video_filename = f"{input_folder_name}.{args.format}"
# # output_video_path = os.path.join(output_folder, video_filename)

# # # Read and Sort Images (Case-Insensitive)
# # image_files = sorted([f for f in os.listdir(args.input) if f.lower().endswith(args.image_format.lower())])

# # if not image_files:
# #     print(f"❌ No images found in '{args.input}' with format '{args.image_format}'!")
# #     exit()

# # # Get Image Dimensions (Default to first image size)
# # first_img_path = os.path.join(args.input, image_files[0])
# # first_img = cv2.imread(first_img_path)

# # if first_img is None:
# #     print(f"❌ Failed to read the first image: {first_img_path}")
# #     exit()

# # height, width, _ = first_img.shape  # Default resolution

# # # Set Custom Resolution If Provided
# # if args.resolution:
# #     try:
# #         width, height = map(int, args.resolution.replace("*", "x").split("x"))
# #     except ValueError:
# #         print("❌ Invalid resolution format! Use WxH (e.g., 1920x1080)")
# #         exit()

# # # Load Logo Image (Even if it's not transparent)
# # logo = cv2.imread(args.logo, cv2.IMREAD_UNCHANGED)

# # if logo is None:
# #     print(f"❌ Failed to load logo image: {args.logo}")
# #     exit()

# # # Resize Logo (15% of video width)
# # logo_width = int(width * 0.15)
# # logo_height = int((logo.shape[0] / logo.shape[1]) * logo_width)
# # logo = cv2.resize(logo, (logo_width, logo_height), interpolation=cv2.INTER_AREA)

# # # Convert Logo to RGB (If it has alpha, separate it)
# # if logo.shape[2] == 4:
# #     logo_rgb = logo[:, :, :3]
# #     logo_alpha = logo[:, :, 3] / 255.0  # Normalize alpha
# # else:
# #     logo_rgb = logo
# #     logo_alpha = np.ones((logo.shape[0], logo.shape[1]), dtype=np.float32)  # Full opacity

# # # Video Writer Setup
# # fourcc = cv2.VideoWriter_fourcc(*"mp4v")
# # video_writer = cv2.VideoWriter(output_video_path, fourcc, args.fps, (width, height))

# # # Mapping User Input to OpenCV Font
# # font_mapping = {
# #     "SIMPLEX": cv2.FONT_HERSHEY_SIMPLEX,
# #     "PLAIN": cv2.FONT_HERSHEY_PLAIN,
# #     "DUPLEX": cv2.FONT_HERSHEY_DUPLEX,
# #     "COMPLEX": cv2.FONT_HERSHEY_COMPLEX,
# #     "TRIPLEX": cv2.FONT_HERSHEY_TRIPLEX,
# #     "ITALIC": cv2.FONT_HERSHEY_SCRIPT_SIMPLEX  # Italic ek special case
# # }

# # # Get Selected Font
# # font = font_mapping[args.watermark_font]

# # # Process Each Frame
# # for img_name in image_files:
# #     img_path = os.path.join(args.input, img_name)
# #     frame = cv2.imread(img_path)

# #     if frame is None:
# #         print(f"⚠️ Skipping corrupted/missing image: {img_path}")
# #         continue

# #     # Resize Frame If Custom Resolution is Given
# #     if args.resolution:
# #         frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)

# #     # Define Logo Position Based on User Input
# #     if args.position == "top-left":
# #         x_offset, y_offset = 20, 20
# #     elif args.position == "top-right":
# #         x_offset, y_offset = width - logo_width - 20, 20
# #     elif args.position == "bottom-left":
# #         x_offset, y_offset = 20, height - logo_height - 20
# #     elif args.position == "bottom-right":
# #         x_offset, y_offset = width - logo_width - 20, height - logo_height - 20

# #     # Extract ROI from Frame (Same Size as Logo)
# #     roi = frame[y_offset:y_offset + logo_height, x_offset:x_offset + logo_width]

# #     # Multiply Blend Logo with Background
# #     blended = cv2.multiply(roi.astype(np.float32), (logo_rgb / 255.0).astype(np.float32)).astype(np.uint8)

# #     # Apply Alpha Mask for Smooth Blend
# #     blended = (blended * logo_alpha[:, :, None] + roi * (1 - logo_alpha[:, :, None])).astype(np.uint8)

# #     # Place Blended Logo Back on Frame
# #     frame[y_offset:y_offset + logo_height, x_offset:x_offset + logo_width] = blended

# #     # Apply Watermark Text
# #     if args.watermark_text:
# #         font_scale = 10
# #         font_thickness = 20
# #         text_size = cv2.getTextSize(args.watermark_text, font, font_scale, font_thickness)[0]
        
# #             # Define Watermark Position
# #     if args.watermark_position == "top-left":
# #         text_x, text_y = 50, 100
# #     elif args.watermark_position == "top-right":
# #         text_x, text_y = width - text_size[0] - 50, 100
# #     elif args.watermark_position == "bottom-left":
# #         text_x, text_y = 50, height - 50
# #     elif args.watermark_position == "bottom-right":
# #         text_x, text_y = width - text_size[0] - 50, height - 50
# #     elif args.watermark_position == "center":
# #         text_x, text_y = (width - text_size[0]) // 2, (height + text_size[1]) // 2

# #         overlay = frame.copy()
        
# #     # **Step 1: Apply Black Outline for Smoother Curves**
# #     for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:  # Outline in 4 directions
# #         cv2.putText(overlay, args.watermark_text, (text_x + dx, text_y + dy), font, font_scale, (110, 110, 110), font_thickness , cv2.LINE_AA)
# #     # **Step 3: Blend Overlay for Smooth Appearance**
# #     frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)  # Less transparency for better visibility

# #     # Write Frame to Video
# #     video_writer.write(frame)

# # video_writer.release()

# # # Get Video Details
# # video_size = os.stat(output_video_path).st_size / (1024 * 1024)  # Convert bytes to MB
# # cap = cv2.VideoCapture(output_video_path)

# # if not cap.isOpened():
# #     print("❌ Error opening video file")
# # else:
# #     frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
# #     duration = frame_count / args.fps  # Total video duration in seconds
# #     bitrate = (video_size * 8) / duration if duration > 0 else 0  # Bitrate in Mbps

# #     print(f"✅ Video Created: {output_video_path}")
# #     print(f"📏 Resolution: {width}x{height}")
# #     print(f"🎞️ Frame Count: {frame_count}")
# #     print(f"⏳ Duration: {duration:.2f} seconds")
# #     print(f"🎥 FPS: {args.fps}")
# #     print(f"📂 File Size: {video_size:.2f} MB")
# #     print(f"🔧 Bitrate: {bitrate:.2f} Mbps")  

# # cap.release()


# import os
# import argparse
# import cv2
# import numpy as np

# # Argument Parser Setup
# parser = argparse.ArgumentParser(description="Generate Video with Logo Overlay and Watermark")
# parser.add_argument("-i", "--input", required=True, help="Input folder path")
# parser.add_argument("-o", "--output", required=True, help="Output folder path")
# parser.add_argument("-f", "--format", required=True, choices=["mp4", "mov"], help="Video format")
# parser.add_argument("--fps", type=int, default=30, help="Frames per second (default: 30)")
# parser.add_argument("-imgf", "--image_format", required=True, choices=["jpg", "jpeg", "png", "webp"], help="Input image format")
# parser.add_argument("-l", "--logo", required=True, help="Company logo (PNG)")
# parser.add_argument("-res", "--resolution", help="Custom resolution in WxH format (e.g., 1920x1080)")
# parser.add_argument("-p", "--position", required=True, choices=["top-left", "top-right", "bottom-left", "bottom-right"], help="Logo position in video")
# parser.add_argument("-wt", "--watermark_text", help="Watermark text to overlay on the video")
# parser.add_argument("-wtf", "--watermark_font", required=True, choices=["SIMPLEX", "PLAIN", "DUPLEX", "COMPLEX", "TRIPLEX", "ITALIC"], help="Watermark text font type")
# parser.add_argument("-wtp", "--watermark_position", required=True, choices=["top-left", "top-right", "bottom-left", "bottom-right", "center","cross"], help="Watermark text position")

# args = parser.parse_args()

# # Ensure Output Folder Exists
# output_folder = args.output
# os.makedirs(output_folder, exist_ok=True)

# # Construct Output Video Path
# input_folder_name = os.path.basename(os.path.normpath(args.input))
# video_filename = f"{input_folder_name}.{args.format}"
# output_video_path = os.path.join(output_folder, video_filename)

# # Read and Sort Images (Case-Insensitive)
# image_files = sorted([f for f in os.listdir(args.input) if f.lower().endswith(args.image_format.lower())])

# if not image_files:
#     print(f"❌ No images found in '{args.input}' with format '{args.image_format}'!")
#     exit()

# # Get Image Dimensions (Default to first image size)
# first_img_path = os.path.join(args.input, image_files[0])
# first_img = cv2.imread(first_img_path)

# if first_img is None:
#     print(f"❌ Failed to read the first image: {first_img_path}")
#     exit()

# height, width, _ = first_img.shape  # Default resolution

# # Set Custom Resolution If Provided
# if args.resolution:
#     try:
#         width, height = map(int, args.resolution.replace("*", "x").split("x"))
#     except ValueError:
#         print("❌ Invalid resolution format! Use WxH (e.g., 1920x1080)")
#         exit()


# # Load Logo Image
# logo = cv2.imread(args.logo, cv2.IMREAD_UNCHANGED)

# if logo is None:
#     print(f"❌ Failed to load logo image: {args.logo}")
#     exit()

# # Resize Logo (15% of video width)
# logo_width = int(width * 0.15)
# logo_height = int((logo.shape[0] / logo.shape[1]) * logo_width)
# logo = cv2.resize(logo, (logo_width, logo_height), interpolation=cv2.INTER_AREA)

# # Convert Logo to RGB (If it has alpha, separate it)
# if logo.shape[2] == 4:
#     logo_rgb = logo[:, :, :3]
#     logo_alpha = logo[:, :, 3] / 255.0  # Normalize alpha
# else:
#     logo_rgb = logo
#     logo_alpha = np.ones((logo.shape[0], logo.shape[1]), dtype=np.float32)  # Full opacity

# # Video Writer Setup
# fourcc = cv2.VideoWriter_fourcc(*"mp4v")
# video_writer = cv2.VideoWriter(output_video_path, fourcc, args.fps, (width, height))

# # Mapping User Input to OpenCV Font
# font_mapping = {
#     "SIMPLEX": cv2.FONT_HERSHEY_SIMPLEX,
#     "PLAIN": cv2.FONT_HERSHEY_PLAIN,
#     "DUPLEX": cv2.FONT_HERSHEY_DUPLEX,
#     "COMPLEX": cv2.FONT_HERSHEY_COMPLEX,
#     "TRIPLEX": cv2.FONT_HERSHEY_TRIPLEX,
#     "ITALIC": cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
# }

# # Get Selected Font
# font = font_mapping[args.watermark_font]

# # Process Each Frame
# for img_name in image_files:
#     img_path = os.path.join(args.input, img_name)
#     frame = cv2.imread(img_path)

#     if frame is None:
#         print(f"⚠️ Skipping corrupted/missing image: {img_path}")
#         continue

#     # Resize Frame If Custom Resolution is Given
#     if args.resolution:
#         frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)

#     # Define Logo Position Based on User Input
#     if args.position == "top-left":
#         x_offset, y_offset = 20, 20
#     elif args.position == "top-right":
#         x_offset, y_offset = width - logo_width - 20, 20
#     elif args.position == "bottom-left":
#         x_offset, y_offset = 20, height - logo_height - 20
#     elif args.position == "bottom-right":
#         x_offset, y_offset = width - logo_width - 20, height - logo_height - 20

#     # Extract ROI from Frame (Same Size as Logo)
#     roi = frame[y_offset:y_offset + logo_height, x_offset:x_offset + logo_width]

#     # Multiply Blend Logo with Background
#     blended = cv2.multiply(roi.astype(np.float32), (logo_rgb / 255.0).astype(np.float32)).astype(np.uint8)

#     # Apply Alpha Mask for Smooth Blend
#     blended = (blended * logo_alpha[:, :, None] + roi * (1 - logo_alpha[:, :, None])).astype(np.uint8)

#     # Place Blended Logo Back on Frame
#     frame[y_offset:y_offset + logo_height, x_offset:x_offset + logo_width] = blended

#     # Apply Watermark Text
#     if args.watermark_text:
#         font_scale = 10
#         font_thickness = 20
#         text_size = cv2.getTextSize(args.watermark_text, font, font_scale, font_thickness)[0]

#         # Define Watermark Position
#         if args.watermark_position == "top-left":
#             text_x, text_y = 50, 100
#         elif args.watermark_position == "top-right":
#             text_x, text_y = width - text_size[0] - 50, 100
#         elif args.watermark_position == "bottom-left":
#             text_x, text_y = 50, height - 50
#         elif args.watermark_position == "bottom-right":
#             text_x, text_y = width - text_size[0] - 50, height - 50
#         elif args.watermark_position == "center":
#             text_x, text_y = (width - text_size[0]) // 2, (height + text_size[1]) // 2
#         elif args.watermark_position == "cross":
#             positions = [
#             (50, 100),  # Top-left
#             (width - text_size[0] - 50, 100),  # Top-right
#             (50, height - 50),  # Bottom-left
#             (width - text_size[0] - 50, height - 50)  # Bottom-right
#         ]
#         overlay = frame.copy()

#         # Apply Black Outline for Better Visibility
#         for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
#             cv2.putText(overlay, args.watermark_text, (text_x + dx, text_y + dy), font, font_scale, (110, 110, 110), font_thickness, cv2.LINE_AA)

#         # Blend Overlay for Smooth Appearance
#         frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)

#     # Write Frame to Video
#     video_writer.write(frame)

# video_writer.release()

# # Get Video Details
# video_size = os.stat(output_video_path).st_size / (1024 * 1024)  # Convert bytes to MB
# cap = cv2.VideoCapture(output_video_path)

# if not cap.isOpened():
#     print("❌ Error opening video file")
# else:
#     frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#     duration = frame_count / args.fps  # Total video duration in seconds
#     bitrate = (video_size * 8) / duration if duration > 0 else 0  # Bitrate in Mbps
    
#     print(f"✅ Video Created: {output_video_path}")
#     print(f"📏 Resolution: {width}x{height}")
#     print(f"🎞️ Frame Count: {frame_count}")
#     print(f"⏳ Duration: {duration:.2f} seconds")
#     print(f"🎥 FPS: {args.fps}")
#     print(f"📂 File Size: {video_size:.2f} MB")
#     print(f"🔧 Bitrate: {bitrate:.2f} Mbps")  


# cap.release()
