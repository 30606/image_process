import argparse
import os
import sys
from PIL import Image
import pillow_avif
from concurrent.futures import ThreadPoolExecutor, as_completed

# **Main Parser Setup**
parser = argparse.ArgumentParser(
    description="Image Format Converter",
    epilog="""
    Example Usage:
      python Convert.py jpeg -i "input_path" -o "output_path" -q quality -t threads -w width --h height -p --opt
      python Convert.py webp -i "input_path" -o "output_path" -q quality -t threads -w width --h height -m method
      python Convert.py avif -i "input_path" -o "output_path" -q quality -t threads -w width --h height -s speed
    """,
    formatter_class=argparse.RawTextHelpFormatter
)
subparsers = parser.add_subparsers(dest="format", required=True, help="Choose image format: jpeg, webp, avif")

# **Common Arguments (General Settings)**
common_parser = argparse.ArgumentParser(add_help=False)
common_parser.add_argument("-i", "-input-path",type=str, required=True,metavar="INPUT-PATH")
common_parser.add_argument("-o", "-output-path", type=str, required=True,metavar="OUTPUT-PATH")
common_parser.add_argument("-t", "-threads", type=int, required=True,metavar="THREADS")

# **Quality Arguments (MUST COME FIRST)**
quality_group = common_parser.add_argument_group("Quality Settings")
quality_group.add_argument("-q", "-quality", type=int, default=100,metavar="QUALITY (1-100, default: 100)")

# **Resize Arguments (AFTER Quality)**
resize_group = common_parser.add_argument_group("Resize Settings")
resize_group.add_argument("-w",  "-width",type=int, required=False,metavar="WIDTH")
resize_group.add_argument("--h", "-height", type=int, required=False,metavar="HEIGHT")

# **JPEG Arguments**
jpeg_parser = subparsers.add_parser("jpeg", parents=[common_parser], help="Convert images to JPEG format")
jpeg_parser.add_argument("-p", "-progressive", type=bool, choices=["true", "false"], metavar="PROGRESSIVE (true/false)", default="false")
jpeg_parser.add_argument("-opt", "-optimize", type=bool, choices=["true", "false"], metavar="OPTIMIZE(true/false)", default="false")

# **WEBP Arguments**
webp_parser = subparsers.add_parser("webp", parents=[common_parser], help="Convert images to WEBP format")
webp_parser.add_argument("-m", "-method", type=int, choices=range(0, 7), required=False, metavar="METHOD (0-6)")

# **AVIF Arguments**
avif_parser = subparsers.add_parser("avif", parents=[common_parser], help="Convert images to AVIF format")
avif_parser.add_argument("-s", "-speed", type=int, choices=range(0, 8), required=False,metavar="SPEED (0-10)", help=" #s Speed (0-10) for AVIF")

# **Parse Arguments**
args = parser.parse_args()

# **Check format before using format-specific arguments**
progressive = args.p if args.format == "jpeg" else False  # Only for JPEG
optimize = args.opt if args.format == "jpeg" else False   # Only for JPE

# **Define Format-Specific Folder**
format_folder = os.path.join(args.o, args.format)
os.makedirs(format_folder, exist_ok=True)

# **Resize Logic Before Conversion**
def resize_image(img):
    if args.w and args.h:
        original_width, original_height = img.size
        if args.w < original_width or args.h < original_height:  # Smaller size only
            img = img.resize((args.w, args.h), Image.LANCZOS)  # Maintain sharpness
    return img

def convert_image(image_path, output_subfolder):
    try:
        filename = os.path.basename(image_path)
        output_file = os.path.join(output_subfolder, os.path.splitext(filename)[0] + f".{args.format}")

        # **Skip Already Converted Files**
        if os.path.exists(output_file):
            return f"⚠️ Skipped (Already Exists): {filename}"

        img = Image.open(image_path).convert("RGBA")

        # **Apply Resize (Only If Needed)**
        img = resize_image(img)

        # **JPEG Conversion**
        if args.format == "jpeg":
            img.convert("RGB").save(output_file, "JPEG", quality=args.q, progressive=progressive, optimize=optimize)

        # **AVIF Conversion**
        elif args.format == "avif":
            img.convert("RGB").save(output_file, "AVIF", quality=args.q, speed=args.s)

        # **WEBP Conversion**
        elif args.format == "webp":
            img.save(output_file, "WEBP", quality=args.q, method=args.m)

        return f"✅ {filename} → {args.format.upper()} ({output_file})"
    
    except Exception as e:
        return f"❌ Error converting {image_path}: {e}"
# **Collect All PNG Files from the Input Folder**
image_files = []
for root, _, files in os.walk(args.i):
    relative_path = os.path.relpath(root, args.i)
    output_subfolder = os.path.join(format_folder, relative_path)
    os.makedirs(output_subfolder, exist_ok=True)
    for filename in files:
        if filename.lower().endswith(".png"):
            image_files.append((os.path.join(root, filename), output_subfolder))

# **Process Images Using Multi-threading**
with ThreadPoolExecutor(max_workers=args.t) as executor:
    future_tasks = {executor.submit(convert_image, img_path, folder): img_path for img_path, folder in image_files}
    for future in as_completed(future_tasks):
        print(future.result())

print(f"\n PNG images successfully converted to {args.format.upper()} format in '{format_folder}'!")
