from PIL import Image, ImageDraw, ImageFont
import random

def draw_fixed_square_grid_with_pillow(image_path, square_size=100):
    # Load the image
    img = Image.open(image_path)
    width, height = img.size
    
    # Calculate how many squares fit into the image width and height
    grid_size_x = width // square_size
    grid_size_y = height // square_size
    
    # Create a white canvas larger than the original image (for padding)
    padded_width = width + 100
    padded_height = height + 100
    padded_img = Image.new("RGB", (padded_width, padded_height), color=(255, 255, 255))
    
    # Paste the original image onto the white canvas
    padded_img.paste(img, (50, 50))
    
    # Get a drawing context
    draw = ImageDraw.Draw(padded_img)
    
    # Draw the grid on the padded image
    for i in range(1, grid_size_x):
        draw.line((50 + i * square_size, 50, 50 + i * square_size, 50 + height), fill=(0, 255, 0), width=2)
    
    for i in range(1, grid_size_y):
        draw.line((50, 50 + i * square_size, 50 + width, 50 + i * square_size), fill=(0, 255, 0), width=2)
    
    # Define font for numbers (use default if font is not available)
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        font = ImageFont.load_default()
    
    # Adjust padding for left-side numbers (raise vertical alignment a bit)
    left_padding = 15  
    for i in range(grid_size_y):
        num_text = str(i)
        text_size = draw.textbbox((0, 0), num_text, font=font)  # Get text size
        text_width = text_size[2] - text_size[0]
        text_height = text_size[3] - text_size[1]

        x_pos = 10
        y_pos = 50 + i * square_size + square_size // 2 - left_padding

        # Draw background rectangle
        bg_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        draw.rectangle([x_pos - 5, y_pos - 5, x_pos + text_width + 5, y_pos + text_height + 5], fill=bg_color)

        # Draw number in white
        draw.text((x_pos, y_pos), num_text, fill=(255, 255, 255), font=font)
    
    # Adjust padding for top row numbers (raise vertical padding a bit)
    top_padding = 15  
    for i in range(grid_size_x):
        num_text = str(i)
        text_size = draw.textbbox((0, 0), num_text, font=font)  # Get text size
        text_width = text_size[2] - text_size[0]
        text_height = text_size[3] - text_size[1]

        x_pos = 50 + i * square_size + square_size // 3
        y_pos = 30 - top_padding

        # Draw background rectangle
        bg_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        draw.rectangle([x_pos - 5, y_pos - 5, x_pos + text_width + 5, y_pos + text_height + 5], fill=bg_color)

        # Draw number in white
        draw.text((x_pos, y_pos), num_text, fill=(255, 255, 255), font=font)
    
    # Show the result
    padded_img.show()
    padded_img.save('./output.png', format='PNG')

# Test the function
image_path = 'test1.png'  # Replace with the path to your image
draw_fixed_square_grid_with_pillow(image_path, square_size=7*7)  # Define square size here
