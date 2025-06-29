from PIL import Image
import cv2
import numpy as np


def enhance_dark_image(
    input_path: str,
    output_path: str,
    clip_limit: float = 2.0,
    tile_grid_size: tuple = (8, 8),
):
    """
    Enhances a dark image using CLAHE (Contrast Limited Adaptive Histogram Equalization).

    Args:
        input_path (str): Path to the input image file.
        output_path (str): Path to save the enhanced image file.
        clip_limit (float): Threshold for contrast limiting. Higher values give more contrast.
        tile_grid_size (tuple): Size of the grid for histogram equalization. (width, height).
    """
    try:
        # 1. Load image using Pillow
        pil_image = Image.open(input_path).convert("RGB")

        # Convert PIL Image to OpenCV format (NumPy array)
        # OpenCV uses BGR by default, Pillow uses RGB
        cv_image = np.array(pil_image)
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)

        # 2. Convert to LAB color space
        # CLAHE works best on the L-channel (lightness)
        lab = cv2.cvtColor(cv_image, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)

        # 3. Apply CLAHE to the L-channel
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        cl = clahe.apply(l_channel)

        # 4. Merge the enhanced L-channel back with A and B channels
        limg = cv2.merge([cl, a_channel, b_channel])

        # 5. Convert back to BGR color space
        enhanced_cv_image = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

        # Convert back to RGB for Pillow saving
        enhanced_pil_image = Image.fromarray(
            cv2.cvtColor(enhanced_cv_image, cv2.COLOR_BGR2RGB)
        )

        # 6. Save the enhanced image using Pillow
        enhanced_pil_image.save(output_path)
        print(f"Image enhanced and saved to {output_path}")

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Example usage (for testing purposes)
    # You would typically call this from main.py or a test script
    # For a real test, you'd need an actual image file
    # enhance_dark_image("input.jpg", "output_enhanced.jpg")
    pass
