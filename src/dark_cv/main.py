import typer
from typing_extensions import Annotated
from typing import Optional, Tuple
from pathlib import Path
from datetime import datetime
import platform
import os

from dark_cv.enhancer import enhance_dark_image
from dark_cv.comparator import create_comparison_image

app = typer.Typer()


def _generate_output_path(
    input_path: Path, timestamp: str, combination_postfix: str
) -> Path:
    return (
        input_path.parent
        / f"{input_path.stem}_{timestamp}_darkcv{combination_postfix}{input_path.suffix}"
    )


@app.command()
def enhance(
    input_path: Annotated[Path, typer.Argument(help="Path to the input image file.")],
    output_path: Annotated[
        Optional[Path],
        typer.Argument(
            help="Path to save the enhanced image file. If not specified, a timestamp and tool-specific postfix will be appended to the input filename."
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
        Tuple[int, int],
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
    retinex: Annotated[
        Optional[bool],
        typer.Option(
            "--retinex/--no-retinex",
            help="Enable/disable Multi-Scale Retinex with Color Restoration (MSRCR). (default: Enabled)",
            rich_help_panel="Enhancement Options",
        ),
    ] = None,
    clahe: Annotated[
        Optional[bool],
        typer.Option(
            "--clahe/--no-clahe",
            help="Enable/disable CLAHE (Contrast Limited Adaptive Histogram Equalization). (default: Enabled)",
            rich_help_panel="Enhancement Options",
        ),
    ] = None,
    compare: Annotated[
        bool,
        typer.Option(
            "--compare/--no-compare",
            help="Create a side-by-side comparison image of original and enhanced. (default: Enabled)",
        ),
    ] = True,
    all_combinations: Annotated[
        bool,
        typer.Option(
            "--all-combinations",
            help="Run all 7 combinations of Denoise, Retinex, and CLAHE.",
            rich_help_panel="Automation Options",
        ),
    ] = False,
):
    """
    Enhance dark images using CLAHE and optional additional techniques.
    """

    # Display system information once at the beginning of the command execution
    typer.echo(
        typer.style("\n--- System Information ---", fg=typer.colors.BLUE, bold=True)
    )
    typer.echo(f"OS: {platform.system()} {platform.release()} ({platform.version()})")
    typer.echo(f"Architecture: {platform.machine()}")
    typer.echo(f"Python Version: {platform.python_version()}")
    typer.echo(f"CPU Cores: {os.cpu_count()}")

    if all_combinations:
        combinations = [
            # Denoise, Retinex, CLAHE
            (True, True, True),  # 1. Denoise: ON, Retinex: ON, CLAHE: ON
            (True, True, False),  # 2. Denoise: ON, Retinex: ON, CLAHE: OFF
            (True, False, True),  # 3. Denoise: ON, Retinex: OFF, CLAHE: ON
            (True, False, False),  # 4. Denoise: ON, Retinex: OFF, CLAHE: OFF
            (False, True, True),  # 5. Denoise: OFF, Retinex: ON, CLAHE: ON
            (False, True, False),  # 6. Denoise: OFF, Retinex: ON, CLAHE: OFF
            (False, False, True),  # 7. Denoise: OFF, Retinex: OFF, CLAHE: ON
        ]

        with typer.progressbar(
            combinations, label="Processing Combinations"
        ) as progress:
            for i, (d, r, c) in enumerate(progress):
                typer.echo(
                    typer.style(
                        f"\n--- Running Combination {i + 1} / {len(combinations)} ---",
                        fg=typer.colors.CYAN,
                        bold=True,
                    )
                )
                current_denoise = d
                current_retinex = r
                current_clahe = c

                # Generate unique output path for each combination
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

                _run_enhancement(
                    input_path=input_path,
                    output_path=None,  # Let _run_enhancement generate the path
                    clip_limit=clip_limit,
                    tile_grid_size=tile_grid_size,
                    denoise=current_denoise,
                    retinex=current_retinex,
                    clahe=current_clahe,
                    compare=compare,
                    _timestamp=timestamp,
                )
    else:
        _run_enhancement(
            input_path=input_path,
            output_path=output_path,
            clip_limit=clip_limit,
            tile_grid_size=tile_grid_size,
            denoise=denoise,
            retinex=retinex,
            clahe=clahe,
            compare=compare,
            # For single run, generate timestamp and postfix here if output_path is None
            _timestamp=datetime.now().strftime("%Y%m%d%H%M%S")
            if output_path is None
            else None,
        )


def _run_enhancement(
    input_path: Path,
    output_path: Optional[Path],
    clip_limit: float,
    tile_grid_size: Tuple[int, int],
    denoise: Optional[bool],
    retinex: Optional[bool],
    clahe: Optional[bool],
    compare: bool,
    _timestamp: Optional[str] = None,  # Internal parameter for all_combinations
):
    """
    Helper function to run a single enhancement process.
    """
    # Determine actual boolean values for processing
    actual_denoise = True if denoise is None else denoise
    actual_retinex = True if retinex is None else retinex
    actual_clahe = True if clahe is None else clahe

    # Generate combination postfix based on actual applied processes
    postfix_parts = []
    if actual_denoise:
        postfix_parts.append("D")
    if actual_retinex:
        postfix_parts.append("R")
    if actual_clahe:
        postfix_parts.append("C")

    # Use the generated postfix if not part of all_combinations, or if it's empty for all_combinations
    # Otherwise, use the one passed from all_combinations loop
    effective_combination_postfix = (
        "_" + "".join(postfix_parts) if postfix_parts else "_None"
    )

    # If output_path is None, generate it here using provided or new timestamp/postfix
    if output_path is None:
        timestamp = (
            _timestamp if _timestamp else datetime.now().strftime("%Y%m%d%H%M%S")
        )
        output_path = _generate_output_path(
            input_path, timestamp, effective_combination_postfix
        )

    typer.echo(
        typer.style(
            "\n--- Starting Image Enhancement ---", fg=typer.colors.GREEN, bold=True
        )
    )
    typer.echo(f"Input: {input_path}")
    typer.echo(f"Output: {output_path}")

    typer.echo(
        typer.style(
            f"Denoising (Bilateral Filter): {'Enabled' if actual_denoise else 'Disabled'}",
            fg=typer.colors.BRIGHT_YELLOW if actual_denoise else typer.colors.WHITE,
        )
    )
    typer.echo(
        typer.style(
            f"Retinex (MSRCR): {'Enabled' if actual_retinex else 'Disabled'}",
            fg=typer.colors.BRIGHT_YELLOW if actual_retinex else typer.colors.WHITE,
        )
    )
    typer.echo(
        typer.style(
            f"CLAHE: {'Enabled' if actual_clahe else 'Disabled'}",
            fg=typer.colors.BRIGHT_YELLOW if actual_clahe else typer.colors.WHITE,
        )
    )
    if actual_clahe:
        typer.echo(f"  CLAHE Clip Limit: {clip_limit}")
        typer.echo(f"  CLAHE Tile Grid Size: {tile_grid_size}")

    processing_time = enhance_dark_image(
        str(input_path),
        str(output_path),
        clip_limit=clip_limit,
        tile_grid_size=tile_grid_size,
        denoise=actual_denoise,
        use_retinex=actual_retinex,
        use_clahe=actual_clahe,
    )

    # Create comparison image if requested
    if compare:
        caption_params = []
        if actual_denoise:
            caption_params.append("Denoise")
        if actual_retinex:
            caption_params.append("Retinex")
        if actual_clahe:
            caption_params.append(
                f"CLAHE(clip={clip_limit}, grid={tile_grid_size[0]}x{tile_grid_size[1]})"
            )

        caption_text = f"Original vs Enhanced ({', '.join(caption_params) if caption_params else 'No Enhancement Applied'})"

        # Corrected comparison output path
        comparison_output_path = (
            input_path.parent
            / f"{input_path.stem}_{_timestamp}_darkcv{effective_combination_postfix}_compare{input_path.suffix}"
        )

        create_comparison_image(
            input_path, output_path, comparison_output_path, caption_text=caption_text
        )

    typer.echo(
        typer.style("\n--- Processing Complete ---", fg=typer.colors.GREEN, bold=True)
    )
    typer.echo(
        typer.style(
            f"Processing Time: {processing_time:.4f} seconds", fg=typer.colors.GREEN
        )
    )


if __name__ == "__main__":
    app()
