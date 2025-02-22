import sys
import uselect as select
import uasyncio as asyncio
import hub75
import time
import gc


# LED matrix dimensions
HEIGHT = 32
WIDTH = 32

# Initialize the matrix
h75 = hub75.Hub75(WIDTH, HEIGHT, stb_invert=False)

# Start the LED matrix
h75.start()

# def set_color(r, g, b):
#     """
#     Instantly set the LED matrix to a specific RGB color.
#     """
#     print(f"Setting the LED matrix to color RGB({r}, {g}, {b}).")
#     for x in range(WIDTH):
#         for y in range(HEIGHT):
#             h75.set_pixel(x, y, r, g, b)
#     h75.show()  # Make sure to refresh the display after setting the color

def update_matrix(pixel_array):
    """
    Update the LED matrix based on the pixel_array.
    Assumes pixel_array is a flat list of RGB values.
    """
    print("Updating LED matrix with the following pixel array:", pixel_array)
    for i in range(0, len(pixel_array), 3):
        r = pixel_array[i]
        g = pixel_array[i + 1]
        b = pixel_array[i + 2]
        if (i // 3) < (WIDTH * HEIGHT):  # Ensure we do not exceed LED limits
            x = (i // 3) % WIDTH
            y = (i // 3) // WIDTH
            h75.set_pixel(x, y, r, g, b)
            #print(f"Setting LED at ({x}, {y}): R={r}, G={g}, B={b}")

        # Yield control every 32 pixels to prevent blocking
        if i % 96 == 0:
            yield

#     h75.show()  # Update the display to show the new pixel colors

def turn_off():
    """
    Turn off the LED matrix.
    """
    print("Turning off the LED matrix.")
    for x in range(WIDTH):
        for y in range(HEIGHT):
            h75.set_pixel(x, y, 0, 0, 0)
#     h75.show()  # Make sure to refresh the display after turning off

async def process_frame(pixel_data):
    """
    Process the frame data and update the matrix.
    """
    rgb_values = pixel_data.split(',')
    pixel_array = [int(value) for value in rgb_values]
    for _ in update_matrix(pixel_array):
        await asyncio.sleep(0)
    gc.collect()  # Force garbage collection after updating


async def serial_echo():
    """
    Continuously listen for serial input and process commands.
    """
    poll = select.poll()
    poll.register(sys.stdin, select.POLLIN)

    while True:
        events = poll.poll(0)
        if events:
            line = sys.stdin.readline().strip()  # Read an entire line
            if line.startswith("frame"):
                pixel_data = line[line.index('[') + 1:line.index(']')]
                await process_frame(pixel_data)
        await asyncio.sleep(0)

async def main():
    """
    Main entry point for the asyncio loop.
    """
    try:
        await serial_echo()
    except MemoryError:
        print("Memory error occurred. Cleaning up...")
        turn_off()
        gc.collect()
        # Optionally, restart the main loop
        await main()

# Run the asyncio event loop
try:
    asyncio.run(main())
except Exception as e:
    print(f"An error occurred: {e}")
    turn_off()



