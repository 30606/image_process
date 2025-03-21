
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