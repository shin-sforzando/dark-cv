from PIL import Image
import cv2
import numpy as np
import time
from retinex import msrcr


def apply_bilateral_filter(image: np.ndarray) -> np.ndarray:
    """
    Applies a bilateral filter for noise reduction while preserving edges.
    """
    return cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)


def enhance_dark_image(
    input_path: str,
    output_path: str,
    clip_limit: float = 2.0,
    tile_grid_size: tuple = (8, 8),
    denoise: bool = False,
    use_retinex: bool = False,
    use_clahe: bool = True,
) -> float:
    """
    Enhances a dark image using CLAHE and optionally bilateral filtering and Retinex.

    Args:
        input_path (str): Path to the input image file.
        output_path (str): Path to save the enhanced image file.
        clip_limit (float): Threshold for contrast limiting. Higher values give more contrast.
        tile_grid_size (tuple): Size of the grid for histogram equalization. (width, height).
        denoise (bool): If True, applies bilateral filter for noise reduction.
        use_retinex (bool): If True, applies Multi-Scale Retinex with Color Restoration (MSRCR).
        use_clahe (bool): If True, applies CLAHE (Contrast Limited Adaptive Histogram Equalization).

    Returns:
        float: The time taken for the image processing in seconds.
    """
    start_time = time.time()

    try:
        # 1. Load image using Pillow
        pil_image = Image.open(input_path).convert("RGB")
        cv_image = np.array(pil_image)
        # OpenCV uses BGR by default, Pillow uses RGB
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)

        processed_image = cv_image.copy()

        # 2. Apply Denoising (if enabled) - typically before contrast enhancement
        if denoise:
            processed_image = apply_bilateral_filter(processed_image)

        # 3. Apply Retinex (if enabled)
        if use_retinex:
            # MSRCR expects RGB image, so convert back temporarily
            processed_image_rgb = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
            processed_image_retinex = msrcr(
                processed_image_rgb,
                sigmas=[15, 80, 250],
            )
            # Convert back to BGR for CLAHE
            processed_image = cv2.cvtColor(processed_image_retinex, cv2.COLOR_RGB2BGR)

        # 4. Apply CLAHE (if enabled)
        if use_clahe:
            lab = cv2.cvtColor(processed_image, cv2.COLOR_BGR2LAB)
            l_channel, a_channel, b_channel = cv2.split(lab)

            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
            cl = clahe.apply(l_channel)

            limg = cv2.merge([cl, a_channel, b_channel])
            processed_image = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

        # Convert back to RGB for Pillow saving
        enhanced_pil_image = Image.fromarray(
            cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
        )

        # 5. Save the enhanced image using Pillow
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
