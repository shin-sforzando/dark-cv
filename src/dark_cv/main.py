import typer
from typing_extensions import Annotated
from typing import Optional
from pathlib import Path
from datetime import datetime

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
):
    """
    Enhance dark images using CLAHE (Contrast Limited Adaptive Histogram Equalization).
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = (
            input_path.parent / f"{input_path.stem}_{timestamp}{input_path.suffix}"
        )

    enhance_dark_image(
        str(input_path),
        str(output_path),
        clip_limit=clip_limit,
        tile_grid_size=tile_grid_size,
    )


if __name__ == "__main__":
    app()
