import cv2
import numpy as np
import pywt


def apply_bilateral_filter(image: np.ndarray) -> np.ndarray:
    """
    Applies a bilateral filter for noise reduction while preserving edges.
    """
    return cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)


def apply_wavelet_denoise(image: np.ndarray) -> np.ndarray:
    if len(image.shape) == 3:
        b, g, r = cv2.split(image)
        denoised_channels = []
        for channel in [b, g, r]:
            coeffs = pywt.wavedec2(channel, "haar", level=3)
            cA, details = coeffs[0], coeffs[1:]

            denoised_details = []
            for cH, cV, cD in details:
                sigma = np.median(np.abs(cD)) / 0.6745
                threshold = sigma * np.sqrt(2 * np.log(channel.size))

                cH_t = pywt.threshold(cH, threshold, mode="soft")
                cV_t = pywt.threshold(cV, threshold, mode="soft")
                cD_t = pywt.threshold(cD, threshold, mode="soft")
                denoised_details.append((cH_t, cV_t, cD_t))

            denoised_channel = pywt.waverec2([cA] + denoised_details, "haar")
            denoised_channels.append(np.clip(denoised_channel, 0, 255).astype(np.uint8))
        return cv2.merge(denoised_channels)
    else:
        # Original grayscale denoising logic
        coeffs = pywt.wavedec2(image, "haar", level=3)
        cA, details = coeffs[0], coeffs[1:]

        denoised_details = []
        for cH, cV, cD in details:
            sigma = np.median(np.abs(cD)) / 0.6745
            threshold = sigma * np.sqrt(2 * np.log(image.size))

            cH_t = pywt.threshold(cH, threshold, mode="soft")
            cV_t = pywt.threshold(cV, threshold, mode="soft")
            cD_t = pywt.threshold(cD, threshold, mode="soft")
            denoised_details.append((cH_t, cV_t, cD_t))

        denoised_gray = pywt.waverec2([cA] + denoised_details, "haar")
        return np.clip(denoised_gray, 0, 255).astype(np.uint8)


def apply_conditional_denoise(image: np.ndarray) -> np.ndarray:
    # Convert to grayscale for edge detection
    if len(image.shape) == 3:
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray_image = image

    # Canny edge detection
    edges = cv2.Canny(gray_image, 50, 150)

    # Create mask: non-edge regions are targets for denoising
    mask = cv2.bitwise_not(edges)

    # Expand mask to 3 channels if original image is color
    if len(image.shape) == 3:
        mask_3_channel = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    else:
        mask_3_channel = mask

    # Apply bilateral filter to the entire image
    denoised_full = cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)

    # Blend based on mask
    # Where mask is white (non-edge), use denoised_full
    # Where mask is black (edge), use original image
    denoised_masked_part = cv2.bitwise_and(denoised_full, mask_3_channel)
    original_masked_part = cv2.bitwise_and(image, cv2.bitwise_not(mask_3_channel))

    final_denoised_img = cv2.add(denoised_masked_part, original_masked_part)
    return final_denoised_img
