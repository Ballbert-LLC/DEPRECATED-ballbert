from PIL import Image
import os


def resize_images_in_directory(directory_path):
    # Get a list of all files in the directory
    file_list = os.listdir(directory_path)

    for filename in file_list:
        # Get the full path of the image
        input_path = os.path.join(directory_path, filename)

        # Check if it's a file and an image (you can add more checks here if needed)
        if os.path.isfile(input_path) and filename.lower().endswith(
            (".png", ".jpg", ".jpeg", ".gif")
        ):
            # Open the image using Pillow
            image = Image.open(input_path)

            # Get the new size (half the original dimensions)
            new_width = int(image.width / 2)
            new_height = int(image.height / 2)

            # Resize the image in place
            image.thumbnail((new_width, new_height))

            # Save the resized image, overwriting the original image
            image.save(input_path)

            # Close the image to free up memory
            image.close()


if __name__ == "__main__":
    input_directory = "A:\hal\GUI\BA"
    resize_images_in_directory(input_directory)
