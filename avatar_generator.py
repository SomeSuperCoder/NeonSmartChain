from PIL import Image, ImageDraw
import hashlib
import random


def generate_identicon(eth_address, size=8):
    # Create a hash from the ethereum address
    hashed_address = hashlib.sha256(eth_address.lower().encode('utf-8')).hexdigest()

    # Create a seed to make the generation deterministic
    random.seed(int(hashed_address, 16))

    # Create an image with mode 'RGB'
    img_size = size * 10  # Each block is 10x10 pixels
    image = Image.new('RGB', (img_size, img_size), color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    draw = ImageDraw.Draw(image)

    # Iterate over half the blocks (horizontally), the other half will be mirrored
    for x in range(size // 2):
        for y in range(size):
            # Generate a random color
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

            # Only draw a block color if the randomly generated number is even
            if random.randint(0, 1) == 0:
                # Draw on the left side
                draw.rectangle([x * 10, y * 10, (x + 1) * 10, (y + 1) * 10], fill=color)
                # Mirror the block draw on the right side
                draw.rectangle([(size - x - 1) * 10, y * 10, (size - x) * 10, (y + 1) * 10], fill=color)

    # Save and show the generated identicon
    # image.save(f'{eth_address}_identicon.png')
    return image


eth_address = input("Enter the Ethereum wallet address: ").strip()
generate_identicon(eth_address)
