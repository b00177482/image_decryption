import math
import argparse
from collections import Counter
from PIL import Image, ImageDraw

class ECBImageProcessor:
    def __init__(self, image_path, block_size=16, max_colors=254, flip=True, pixels_per_block=16):
        self.image_path = image_path
        self.block_size = block_size
        self.max_colors = max_colors
        self.flip = flip
        self.pixels_per_block = pixels_per_block

    def read_image_bytes(self):
        with open(self.image_path, "rb") as img_file:
            img_data = img_file.read()
        return img_data[:len(img_data) - (len(img_data) % self.block_size)]

    def break_into_blocks(self, img_data):
        return [img_data[i:i + self.block_size] for i in range(0, len(img_data), self.block_size)]

    def count_block_frequencies(self, img_blocks):
        return Counter(img_blocks)

    def generate_color_palette(self):
        color_palette = [tuple((255, 255, 255))]  # Start with white
        for i in range(1, self.max_colors - 1):
            color = (i * 50 % 255, i * 80 % 255, i * 110 % 255)
            color_palette.append(color)
        color_palette.append((0, 0, 0))  # Black as the last color
        return color_palette

    def assign_colors_to_blocks(self, block_frequencies, color_palette):

        sorted_blocks = sorted(block_frequencies.items(), key=lambda x: x[1], reverse=True)
        block_color_map = {}

        for i, (block, _) in enumerate(sorted_blocks):
            if i < len(color_palette) - 1:
                block_color_map[block] = color_palette[i]
            else:
                block_color_map[block] = (0, 0, 0)  # Use black for less frequent blocks

        return block_color_map

    def map_blocks_to_colors(self, img_blocks, block_color_map):

        pixel_colors = []
        for block in img_blocks:
            color = block_color_map.get(block, (0, 0, 0))  # Default to black if block not found
            for _ in range(self.block_size // self.pixels_per_block):
                pixel_colors.append(color)
        return pixel_colors

    def create_image(self, pixel_colors):

        total_pixels = len(pixel_colors)
        img_width = int(math.sqrt(total_pixels))
        img_height = total_pixels // img_width

        if total_pixels % img_width != 0:
            img_height += 1

        # Create a new image and assign pixel colors
        img_output = Image.new('RGB', (img_width, img_height))
        draw_image = ImageDraw.Draw(img_output)

        for idx, color in enumerate(pixel_colors):
            x_coord = idx % img_width
            y_coord = idx // img_width
            if self.flip:
                y_coord = img_height - y_coord - 1  # Flip the y-coordinate
            if y_coord < img_height:
                draw_image.point((x_coord, y_coord), color)

        # Save the generated image
        output_image_path = f"{self.image_path}_image.png"
        img_output.save(output_image_path)

        print(f"Image saved to {output_image_path}")

    def process_image(self):
        """Main method to process the image."""
        img_data = self.read_image_bytes()
        img_blocks = self.break_into_blocks(img_data)
        block_frequencies = self.count_block_frequencies(img_blocks)
        color_palette = self.generate_color_palette()
        block_color_map = self.assign_colors_to_blocks(block_frequencies, color_palette)
        pixel_colors = self.map_blocks_to_colors(img_blocks, block_color_map)
        self.create_image(pixel_colors)


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="ECB Image Decryptor")
    parser.add_argument("image_path", help="Path to the encrypted image file")
    parser.add_argument("--block_size", type=int, default=16, help="Block size (default: 16 bytes)")
    parser.add_argument("--max_colors", type=int, default=254, help="Max colors for the palette (default: 254)")
    parser.add_argument("--flip", type=bool, default=True, help="Flip the image vertically (default: True)")
    parser.add_argument("--pixels_per_block", type=int, default=16, help="Pixels per block for image creation (default: 16)")

    # Parse arguments
    args = parser.parse_args()

    # Create ECBImageProcessor instance with the provided arguments
    processor = ECBImageProcessor(
        image_path=args.image_path,
        block_size=args.block_size,
        max_colors=args.max_colors,
        flip=args.flip,
        pixels_per_block=args.pixels_per_block
    )

    # Process the image
    processor.process_image()
