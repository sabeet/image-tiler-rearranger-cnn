from PIL import Image
import os
import shutil

number_of_slices = 2048

def merge_images_horizontally(image_path1, image_path2, output_path):
    """Merges two images horizontally and saves the result.

    Args:
        image_path1: Path to the first image.
        image_path2: Path to the second image.
        output_path: Path to save the merged image.
    """
    image1 = Image.open(image_path1)
    image2 = Image.open(image_path2)

    width1, height1 = image1.size
    width2, height2 = image2.size

    merged_width = width1 + width2
    merged_height = max(height1, height2)

    merged_image = Image.new("RGB", (merged_width, merged_height))

    merged_image.paste(image1, (0, 0))
    merged_image.paste(image2, (width1, 0))

    merged_image.save(output_path)

def stitch_images_vertically(image_list):
    """
    Stitch multiple images together vertically.

    Parameters:
    image_list (list): List of PIL.Image objects to stitch

    Returns:
    PIL.Image: Combined image
    """
    # Calculate total height and max width
    total_height = sum(img.height for img in image_list)
    max_width = max(img.width for img in image_list)

    # Create new image
    combined = Image.new('RGB', (max_width, total_height))

    # Paste images top to bottom
    y_offset = 0
    for img in image_list:
        combined.paste(img, (0, y_offset))
        y_offset += img.height

    return combined

def stitch_images_horizontally(image_paths):
    """
    Stitch multiple images together horizontally.

    Parameters:
    image_paths (list): List of paths to images to stitch

    Returns:
    PIL.Image: Combined image
    """
    # Load all images
    images = [Image.open(path) for path in image_paths]

    # Calculate total width and max height
    total_width = sum(img.width for img in images)
    max_height = max(img.height for img in images)

    # Create new image with combined width
    combined = Image.new('RGB', (total_width, max_height))

    # Paste images side by side
    x_offset = 0
    for img in images:
        combined.paste(img, (x_offset, 0))
        x_offset += img.width

    return combined


def get_numbered_slices(output_dir, even=True):
    """
    Get paths of even or odd numbered slices from output directory.

    Parameters:
    output_dir (str): Directory containing slices
    even (bool): True for even numbered slices, False for odd

    Returns:
    list: Sorted list of paths to matching slices
    """
    # Get all slice files
    files = [f for f in os.listdir(output_dir) if f.startswith('slice_') and f.endswith('.png')]
    # Filter for even or odd numbered slices
    filtered_files = [f for f in files if (int(f.split('_')[1].split('.')[0]) % 2 == 0) == even]
    # Sort numerically
    filtered_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
    return [os.path.join(output_dir, f) for f in filtered_files]


def slice_image_horizontally(image, num_slices, output_dir):
    """
    Slice an image horizontally into equal pieces and save them to output directory.

    Parameters:
    image (PIL.Image): Image to slice
    num_slices (int): Number of horizontal slices
    output_dir (str): Directory to save slices

    Returns:
    list: List of paths to saved slice images
    """
    # Ensure image is in RGB mode
    if image.mode != 'RGB':
        image = image.convert('RGB')

    width, height = image.size
    # Calculate slice height, ensuring at least 1 pixel per slice
    slice_height = max(1, height // num_slices)
    slice_paths = []

    for i in range(num_slices):
        # Calculate coordinates for this slice
        top = i * slice_height

        # For the last slice, extend to the image edge
        if i == num_slices - 1:
            bottom = height
        else:
            bottom = (i + 1) * slice_height

        # Skip if slice would have zero height
        if bottom <= top:
            continue

        try:
            # Crop the slice
            slice_img = image.crop((0, top, width, bottom))

            # Save the slice
            slice_path = os.path.join(output_dir, f"slice_{i + 1:02d}.png")
            slice_img.save(slice_path)
            slice_paths.append(slice_path)

        except Exception as e:
            print(f"Error processing slice {i + 1}: {e}")
            continue

    if slice_paths:
        print(f"Successfully created {len(slice_paths)} slices")
    else:
        print("No slices were created")

    return slice_paths

def slice_image_vertically(image, num_slices, output_dir):
    """
    Slice an image vertically into equal pieces and save them to output directory.

    Parameters:
    image (PIL.Image): Image to slice
    num_slices (int): Number of vertical slices
    output_dir (str): Directory to save slices

    Returns:
    list: List of paths to saved slice images
    """
    width, height = image.size
    slice_width = width // num_slices
    slice_paths = []

    for i in range(num_slices):
        # Calculate coordinates for this slice
        left = i * slice_width
        # For the last slice, extend to the image edge to handle rounding
        right = width if i == num_slices - 1 else (i + 1) * slice_width

        # Crop the slice
        slice_img = image.crop((left, 0, right, height))

        # Save the slice
        slice_path = os.path.join(output_dir, f"slice_{i + 1:02d}.png")
        slice_img.save(slice_path)
        slice_paths.append(slice_path)

    print("Successfully Sliced")

    return slice_paths

def delete_output_directory(output_dir):
    """
    Safely delete output directory and all its contents.

    Parameters:
    output_dir (str): Path to the output directory

    Returns:
    bool: True if directory was successfully deleted, False if it didn't exist

    Raises:
    Exception: If deletion fails for any other reason
    """
    try:
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
            return True
        return False
    except Exception as e:
        raise Exception(f"Failed to delete output directory: {e}")

def create_output_directory(output_dir):
    """
    Create output directory if it doesn't exist.

    Parameters:
    output_dir (str): Path to the output directory

    Returns:
    str: Path to the created directory
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    except Exception as e:
        raise Exception(f"Failed to create output directory: {e}")

def load_image(image_path):
    """
    Load an image using PIL and perform basic validation.

    Parameters:
    image_path (str): Path to the image file

    Returns:
    PIL.Image: Loaded image object

    Raises:
    FileNotFoundError: If the image file doesn't exist
    IOError: If the file cannot be identified as an image
    """
    # Check if file exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    try:
        # Open the image
        image = Image.open(image_path)

        # Force load the image data
        image.load()

        # Basic image information
        print(f"Image format: {image.format}")
        print(f"Image size: {image.size}")
        print(f"Image mode: {image.mode}")

        return image

    except IOError as e:
        raise IOError(f"Cannot open image file: {e}")

    except Exception as e:
        raise Exception(f"An error occurred while loading the image: {e}")


# Example usage:

try:
    # Clean up any existing output directory
    delete_output_directory("output")

    # Create output directory
    output_dir = create_output_directory("output")

    # Load an image
    image = load_image("example.jpg")

    # Slice images
    slice_paths = slice_image_vertically(image, number_of_slices, output_dir)

    # Get even and odd numbered slices
    even_slices = get_numbered_slices(output_dir, even=True)
    odd_slices = get_numbered_slices(output_dir, even=False)

    # Stitch even and odd slices
    even_combined = stitch_images_horizontally(even_slices)
    odd_combined = stitch_images_horizontally(odd_slices)

    # Save combined images
    even_combined.save(os.path.join(output_dir, "even_combined.png"))
    odd_combined.save(os.path.join(output_dir, "odd_combined.png"))

    # Stitch odd and even combinations horizontally
    final_image = merge_images_horizontally('output/odd_combined.png','output/even_combined.png', 'output/merged_image.jpg')
    final_image_loaded = load_image('output/merged_image.jpg')

    # Rotate image by 90 degrees
    final_image_loaded = final_image_loaded.rotate(90, Image.NEAREST, expand = 1)

    # Slice the combined image horizontally
    vertical_slice = slice_image_vertically(final_image_loaded, number_of_slices, output_dir)

    # Stitch images again
    even_slices = get_numbered_slices(output_dir, even=True)
    odd_slices = get_numbered_slices(output_dir, even=False)

    # Stitch even and odd slices
    even_combined = stitch_images_horizontally(even_slices)
    odd_combined = stitch_images_horizontally(odd_slices)

    even_combined.save('output/even_combined.png')
    odd_combined.save('output/odd_combined.png')

    # Merge the images again
    result_image = merge_images_horizontally('output/odd_combined.png','output/even_combined.png','output/merged_image.jpg')

    # Display the merged image
    merged_image = load_image('output/merged_image.jpg')
    merged_image = merged_image.rotate(270, expand=1)
    merged_image.show()

    # Remove directory after completion
    delete_output_directory("output")

except Exception as e:
    print(f"Error: {e}")
