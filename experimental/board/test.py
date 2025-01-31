from PIL import Image, ImageDraw, ImageFont

def create_labeled_grid(image_path, square_size=100):
    # Load the image (convert to RGBA for transparency support)
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size

    # Calculate grid dimensions
    grid_size_x = width // square_size
    grid_size_y = (height // square_size)+1

    # Create an overlay image for transparent squares
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))  # Fully transparent

    # Create a drawing context for overlay
    draw = ImageDraw.Draw(overlay)

    # Define font for labels (smaller to avoid overlap)
    try:
        font = ImageFont.truetype("arial.ttf", 10)  # Reduced font size
    except IOError:
        font = ImageFont.load_default()

    # Generate labeled transparent squares
    for row in range(grid_size_y):
        for col in range(grid_size_x):
            # Get row label (A, B, C, ...)
            row_label = chr(65 + row)  # ASCII 65 = 'A'
            col_label = str(col + 1)  # Columns are numbered from 1
            label = f"{row_label}{col_label}"

            # Calculate square position
            x1, y1 = col * square_size, row * square_size
            x2, y2 = x1 + square_size, y1 + square_size

            # Draw a **transparent** square with just a border
            draw.rectangle([x1, y1, x2, y2], outline="black", width=2)  # Only border, no fill

            # Position label in **top-left corner** with small padding
            text_x = x1 + 5  # Left padding
            text_y = y1 + 5  # Top padding

            # Draw the label in white background with black text
            text_bg_size = font.getbbox(label)  # Get text bounding box
            text_bg_w = text_bg_size[2] - text_bg_size[0] + 6  # Add some padding
            text_bg_h = text_bg_size[3] - text_bg_size[1] + 4

            # Draw a small rectangle behind the text for better visibility
            draw.rectangle([text_x - 2, text_y - 2, text_x + text_bg_w, text_y + text_bg_h], fill=(255, 255, 255, 80))  # Semi-transparent white
            draw.text((text_x, text_y), label, fill="white", font=font)  # Black text

    # Merge overlay with the original image
    combined = Image.alpha_composite(img, overlay)

    # Save and show the result
    combined.convert("RGB").save("output.png")  # Convert back to RGB for saving
    combined.show()

# Example usage
image_path = "test1.png"  # Replace with your image
create_labeled_grid(image_path, square_size=4*8)  # Adjust square size as needed
