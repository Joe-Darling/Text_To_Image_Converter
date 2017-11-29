"""
name: data_to_image.py
author: Joe Darling
date: 3/9/2017
description: This module writes text into a bitmap file so that the user can see what various words or phrases
physically look like.

The program doesn't always render the file properly so that your browser can view it, which I will fix soon. However you
can use this website http://www.pictureresize.org/online-images-converter.html to view it if it doesn't render on your
computer, this has always worked in my experience.
"""
import math


def create_header_data(width, height, data_len):
    """
    This function creates the header file for a bitmap image using the guidelines found at
    http://www.dragonwins.com/domains/getteched/bmp/bmpfileformat.htm

    :param data_len: Length of the data to be converted into a file
    :param width: The width of the header
    :param height: The height of the header
    :return: A header header file
    """

    HEADER_SIZE = 40     # Header size is always 40 bytes
    START_OFFSET = 54    # The full header (file + image) is 54 bytes
    PLANES = 1           # Number of planes in image, always equal to 1
    BITS_PER_PIXEL = 24  # Our images will be 24-bit images
    IMAGE_DATA_SIZE = 3  # Each pixel has 3 pieces of data, the respective RGB values.
    RESOLUTION_1 = 196   # Recommendation for display, not technically necessary
    RESOLUTION_2 = 14    # Recommendation for display, not technically necessary

    # Initialized list early so that I don't have to set the indexes for bytes with no data later.
    header = [bin(0)] * 54

    # Signature
    header[0] = "B"
    header[1] = "M"

    # File Size in bytes. Slots 2-5 are used as 7 bit binary numbers. (It's actually 8 bit but depending on what program
    # opens the bitmap image, it may read the number as signed, so to avoid this we only use the last 7 bits) This
    # means the picture size can be at most 268 million bytes, which is plenty. We get the number into the 4 bytes by
    # cutting the total binary number up by 7's and piecing it into each index.
    binary = bin(data_len)
    for x in range(2, 6):
        if len(binary) > 7:
            header[x] = binary[:7]
            binary = binary[7:]
        else:
            header[x] = binary
            break

    # Offset to start data
    header[10] = chr(START_OFFSET)

    # Size of image header in bytes
    header[14] = chr(HEADER_SIZE)

    # Image Width in pixels. Pretty much the same explanation as the file size.
    binary = bin(width)
    for x in range(18, 22):
        if len(binary) > 7:
            header[x] = binary[:7]
            binary = binary[7:]
        else:
            header[x] = binary
            break

    # Image Height in pixels. Pretty much the same explanation as the file size.
    binary = bin(height)
    for x in range(22, 26):
        if len(binary) > 7:
            header[x] = binary[:7]
            binary = binary[7:]
        else:
            header[x] = binary
            break

    # Planes in image
    header[26] = chr(PLANES)

    # Bits per pixel
    header[28] = chr(BITS_PER_PIXEL)

    # Size of image data in bytes
    header[34] = chr(IMAGE_DATA_SIZE)

    # Horizontal resolution in pixels per meter
    header[40] = chr(RESOLUTION_1)
    header[41] = chr(RESOLUTION_2)

    # Vertical resolution in pixels per meter
    header[44] = chr(RESOLUTION_1)
    header[45] = chr(RESOLUTION_2)

    return header


def get_dimensions(total_len, power):
    """
    This function attempts to "squarify" the image as much as possible by finding all the multiples the shape can take
    and returning the smallest difference between them as width and height
    :param power: What powers the dimensions will check for. ex (1, 4 etc.)
    :param total_len: Total amount of bytes in image
    :return: the smallest difference in the dimensions as ints width and height
    """

    dimension_compliments = []
    lower_compliment = power
    upper_compliment = total_len
    if total_len == 1:  # In the event of single pixel words, 1 by 1 is the only possible combination
        return 1, 1
    while lower_compliment <= upper_compliment:
        if float(total_len / lower_compliment).is_integer():
            upper_compliment = int(total_len / lower_compliment)
            dimension_compliments.append([lower_compliment, upper_compliment])
        lower_compliment += power

    for dimension in dimension_compliments:
        print(dimension[0], dimension[1])
    return dimension_compliments[-1][0], dimension_compliments[-1][1]


def write_data_to_file(file_data, file, width):
    """
    This function writes the file data to the file and adds correct padding based on width
    :param file_data: The data to be written
    :param file: The file to write it to
    :param width: The width of each line in pixels
    :return: None
    """

    # First we get the padding necessary for the end of each line
    pixels_per_line = width * 3
    padding = ""
    while pixels_per_line % 4 != 0:
        padding += chr(0)
        pixels_per_line += 1

    # Then we write the data 3 units at a time (3 units being one pixel) until we run out of data
    # We finish the file off with null units.
    pixels_per_line = width * 3
    line_width = pixels_per_line + len(padding)
    line = ""
    while len(file_data) > 0:
        if len(file_data) <= 3:  # If there are less than 3 units left in the file we just add the rest to the file
            padding_needed = 3 - len(file_data)
            pads = ""
            while padding_needed > 0:
                pads += chr(0)
                padding_needed -= 1
            line += file_data + pads
            while len(line) < line_width:
                line += chr(0)
            file.write(line)
            break
        else:  # Otherwise we add the next 3 values and write them once the line to be written exceeds pixels per line
            line += file_data[0:3]
            file_data = file_data[3:]
            if len(line) + 3 > pixels_per_line:
                file.write(line + padding)
                line = ""


def create_bitmap(file_data, squarify=False, file_name="new image"):
    """
    This function creates a header image using data from file_data.
    :param file_name: The name of the file the bitmap will write to excluding the .bmp suffix.
    :param squarify: How the image will be drawn, false for regular or true for as close as possible to a square
    :param file_data: file of data to be converted to image
    :return: The Completed file
    """

    # Determines the total number of pixels. One pixel can hold three characters meaning the total
    # can be found with len(data)/3, we then round up so no data is lost.
    total_pixels = math.ceil(len(file_data) / 3)

    if squarify:
        width, height = get_dimensions(total_pixels, 1)
    else:
        # if we aren't making the image a square, since we need each row of pixels to be a multiple of four for padding
        # reasons, we add a blank character to the end of the string until it contains enough pixels to be a power of 4
        while len(file_data) / 3 % 4 != 0:
            file_data += chr(0)
        total_pixels = math.ceil(len(file_data) / 3)
        width, height = get_dimensions(total_pixels, 4)

    # Check the the image to make sure the image to be created isn't too big.
    if width > 268435455 or height > 268435455:
        raise Exception("The image you tried to create is too large, try using a smaller file.")

    # Get header info
    header = create_header_data(width, height, len(file_data))

    # Even though the doc says not to use the file extension I got you guys.
    if file_name[-4:] == ".bmp":
        file_name = file_name[:-4]
    file = open(file_name + ".bmp", "w")

    for c in header:
        try:
            file.write(chr(int(c, 2)))  # If value is an int, cast to char and write to file
        except ValueError:
            file.write(c)  # Otherwise write the already casted char to file

    write_data_to_file(file_data, file, width)
    print("Done.")
    file.close()
