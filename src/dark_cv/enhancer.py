from PIL import Image
import cv2
import numpy as np
import time


def apply_bilateral_filter(image: np.ndarray) -> np.ndarray:
    """
    Applies a bilateral filter for noise reduction while preserving edges.
    """
    # d: Diameter of each pixel neighborhood that is used during filtering.
    # sigmaColor: Filter sigma in the color space. Larger value means that
    #             farther colors within the pixel neighborhood (see sigmaSpace)
    #             will be mixed together.
    # sigmaSpace: Filter sigma in the coordinate space. Larger value means that
    #             farther pixels will influence each other as long as their
    #             colors are close enough (see sigmaColor).
    return cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)


def enhance_dark_image(
    input_path: str,
    output_path: str,
    clip_limit: float = 2.0,
    tile_grid_size: tuple = (8, 8),
    denoise: bool = False,
) -> float:
    """
    Enhances a dark image using CLAHE and optionally bilateral filtering.

    Args:
        input_path (str): Path to the input image file.
        output_path (str): Path to save the enhanced image file.
        clip_limit (float): Threshold for contrast limiting. Higher values give more contrast.
        tile_grid_size (tuple): Size of the grid for histogram equalization. (width, height).
        denoise (bool): If True, applies bilateral filter for noise reduction.

    Returns:
        float: The time taken for the image processing in seconds.
    """
    start_time = time.time()

    try:
        # 1. Load image using Pillow
        pil_image = Image.open(input_path).convert("RGB")
        cv_image = np.array(pil_image)
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)

        processed_image = cv_image.copy()

        # 2. Apply Denoising (if enabled) - typically before contrast enhancement
        if denoise:
            processed_image = apply_bilateral_filter(processed_image)

        # 3. Convert to LAB color space and apply CLAHE
        lab = cv2.cvtColor(processed_image, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        cl = clahe.apply(l_channel)

        limg = cv2.merge([cl, a_channel, b_channel])
        enhanced_cv_image = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

        # Convert back to RGB for Pillow saving
        enhanced_pil_image = Image.fromarray(
            cv2.cvtColor(enhanced_cv_image, cv2.COLOR_BGR2RGB)
        )

        # 4. Save the enhanced image using Pillow
        enhanced_pil_image.save(output_path)
        print(f"Image enhanced and saved to {output_path}")

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

    end_time = time.time()
    return end_time - start_time


if __name__ == "__main__":
    pass
