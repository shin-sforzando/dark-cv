import typer
from typing_extensions import Annotated
from typing import Optional
from pathlib import Path
from datetime import datetime
import platform
import os

from dark_cv.enhancer import enhance_dark_image

app = typer.Typer()


@app.command()
def enhance(
    input_path: Annotated[Path, typer.Argument(help="Path to the input image file.")],
    output_path: Annotated[
        Optional[Path],
        typer.Argument(
            help="Path to save the enhanced image file. If not specified, a timestamp will be appended to the input filename."
        ),
    ] = None,
    clip_limit: Annotated[
        float,
        typer.Option(
            "--clip-limit",
            help="Threshold for contrast limiting. Higher values give more contrast.",
        ),
    ] = 2.0,
    tile_grid_size: Annotated[
        tuple[int, int],
        typer.Option(
            "--tile-grid-size",
            help="Size of the grid for histogram equalization (width, height).",
            rich_help_panel="CLAHE Options",
        ),
    ] = (8, 8),
    denoise: Annotated[
        Optional[bool],
        typer.Option(
            "--denoise/--no-denoise",
            help="Enable/disable bilateral filter for noise reduction. (default: Enabled)",
            rich_help_panel="Enhancement Options",
        ),
    ] = None,
):
    """
    Enhance dark images using CLAHE and optional additional techniques.
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = (
            input_path.parent / f"{input_path.stem}_{timestamp}{input_path.suffix}"
        )

    print("\n--- Starting Image Enhancement ---")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print(f"CLAHE Clip Limit: {clip_limit}")
    print(f"CLAHE Tile Grid Size: {tile_grid_size}")

    # Adjust denoise based on default/explicit values
    actual_denoise = (
        True if denoise is None else denoise
    )  # Default to True if not specified

    print(
        f"Denoising (Bilateral Filter): {'Enabled' if actual_denoise else 'Disabled'}"
    )

    processing_time = enhance_dark_image(
        str(input_path),
        str(output_path),
        clip_limit=clip_limit,
        tile_grid_size=tile_grid_size,
        denoise=actual_denoise,
    )

    print("\n--- Processing Complete ---")
    print(f"Processing Time: {processing_time:.4f} seconds")
    print("\n--- System Information ---")
    print(f"OS: {platform.system()} {platform.release()} ({platform.version()})")
    print(f"Architecture: {platform.machine()}")
    print(f"Python Version: {platform.python_version()}")
    print(f"CPU Cores: {os.cpu_count()}")


if __name__ == "__main__":
    app()
