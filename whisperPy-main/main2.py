import sys
import uselect as select
import uasyncio as asyncio
import hub75
import time


# LED matrix dimensions
HEIGHT = 32
WIDTH = 32

# Initialize the matrix
h75 = hub75.Hub75(WIDTH, HEIGHT, stb_invert=False)

# Start the LED matrix
h75.start()

def update_matrix(pixel_array):
    """
    Update the LED matrix based on the pixel_array.
    Assumes pixel_array is a flat list of RGB values.
    The size of pixel_array should be WIDTH * HEIGHT * 3 (for R, G, B).
    """
    print("Updating LED matrix with the following pixel array:", pixel_array)

    # Check if the pixel_array has the correct length
    expected_length = WIDTH * HEIGHT * 3
    if len(pixel_array) != expected_length:
        raise ValueError(f"Expected pixel array of length {expected_length}, got {len(pixel_array)}.")

    # Set pixel colors in one go
    for index in range(WIDTH * HEIGHT):
        r = pixel_array[index * 3]
        g = pixel_array[index * 3 + 1]
        b = pixel_array[index * 3 + 2]
        x = index % WIDTH
        y = index // WIDTH
        h75.set_pixel(x, y, r, g, b)

    #h75.show()  # Call show once after setting all pixels


# Create a sample frame of colors for the top half of a 32x32 matrix
def create_custom_frame():
    pixel_array = []
    for y in range(16):  # Top half
        for x in range(32):
            # Assign a color based on the position
            r = int((x / 31) * 255)  # Gradient from 0 to 255
            g = int((y / 15) * 255)  # Gradient from 0 to 255
            b = 0  # Keep blue constant
            pixel_array.extend([r, g, b])  # Add RGB values to the list
    # Fill the rest of the matrix with black
    for y in range(16, 32):
        for x in range(32):
            pixel_array.extend([0, 0, 0])  # Black
    return pixel_array

# Example usage
pixel_array = create_custom_frame()
update_matrix(pixel_array)

async def serial_echo():
    
    poll = select.poll()
    poll.register(sys.stdin, select.POLLIN)

    while True:
        events = poll.poll(0)
        if events:
            line = sys.stdin.readline().strip()  # Read an entire line
            if line.startswith("frame"):
                # Example input: frame[135,206,250,135,206,250,135,206,250,135,206,250]
                pixel_data = line[line.index('[') + 1:line.index(']')]
                rgb_values = pixel_data.split(',')  # Split by comma for individual values
                pixel_array = [int(value) for value in rgb_values]  # Convert to integers

                update_matrix(pixel_array)  # Update the matrix with the pixel array
        await asyncio.sleep(0)

async def main():
    """
    Main entry point for the asyncio loop.
    """
    await serial_echo()

# Run the asyncio event loop
asyncio.run(main())