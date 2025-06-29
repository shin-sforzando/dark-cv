from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Optional


def create_comparison_image(
    original_image_path: Path,
    enhanced_image_path: Path,
    output_comparison_path: Path,
    caption_text: Optional[str] = None,
):
    """
    Creates a side-by-side comparison image of original and enhanced images with a caption.

    Args:
        original_image_path (Path): Path to the original input image.
        enhanced_image_path (Path): Path to the enhanced output image.
        output_comparison_path (Path): Path to save the comparison image.
        caption_text (Optional[str]): Text to add as a caption to the comparison image.
    """
    try:
        pil_original = Image.open(original_image_path).convert("RGB")
        pil_enhanced = Image.open(enhanced_image_path).convert("RGB")

        # Ensure both images have the same height
        width1, height1 = pil_original.size
        width2, height2 = pil_enhanced.size

        if height1 != height2:
            # Resize the taller image to match the shorter one's height
            if height1 > height2:
                pil_original = pil_original.resize(
                    (int(width1 * height2 / height1), height2), Image.Resampling.LANCZOS
                )
            else:
                pil_enhanced = pil_enhanced.resize(
                    (int(width2 * height1 / height2), height1), Image.Resampling.LANCZOS
                )

        # Re-get sizes after potential resize
        width1, height1 = pil_original.size
        width2, height2 = pil_enhanced.size

        # Create a new image with double width and same height
        comparison_image = Image.new("RGB", (width1 + width2, height1))
        comparison_image.paste(pil_original, (0, 0))
        comparison_image.paste(pil_enhanced, (width1, 0))

        if caption_text:
            draw = ImageDraw.Draw(comparison_image)

            # Use default font and larger size
            font = ImageFont.load_default(size=30)  # Increased font size

            text_color = (0, 0, 0)  # Black color for text

            # Calculate text position using getbbox
            bbox = font.getbbox(caption_text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            text_x = (comparison_image.width - text_width) / 2
            text_y = comparison_image.height - text_height - 15  # Adjusted position

            # Draw a solid background for the text for better readability
            # Create a new image for the background to ensure full opacity
            background_height = text_height + 30  # Add padding
            background_image = Image.new(
                "RGB",
                (comparison_image.width, int(background_height)),
                color=(200, 200, 200),
            )

            # Paste the background onto the comparison image
            comparison_image.paste(background_image, (0, int(text_y)))

            # Redraw text on the main image after pasting background
            draw = ImageDraw.Draw(
                comparison_image
            )  # Re-initialize draw object after paste
            draw.text((text_x, text_y), caption_text, font=font, fill=text_color)

        comparison_image.save(output_comparison_path)
        print(f"Comparison image saved to {output_comparison_path}")

    except FileNotFoundError:
        print(
            f"Error: Image file not found for comparison: {original_image_path} or {enhanced_image_path}"
        )
    except Exception as e:
        print(f"An error occurred during comparison image creation: {e}")
