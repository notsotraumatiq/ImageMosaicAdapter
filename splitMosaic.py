# Example Usage:
# input_image = Image.open("input_image.png")
# pixel_data_list = split_image(input_image)

def split_image(input_image):
    pixel_data_list = []

    # Get the size of the input image
    width, height = input_image.size

    # Calculate the size of each individual image (assuming 5x5 grid)
    image_width = (width - 6) // 5
    image_height = (height - 6) // 5

    # Loop through the 5x5 grid and extract each individual image
    for row in range(5):
        for col in range(5):
            # Calculate the coordinates to crop the image
            left = col * (image_width + 1) + 1
            top = row * (image_height + 1) + 1
            right = left + image_width
            bottom = top + image_height

            # Crop the image
            image = input_image.crop((left, top, right, bottom))

            # Get the pixel data
            pixel_data = image.getdata()

            # Append the pixel data to the list
            pixel_data_list.append(pixel_data)

    return pixel_data_list
