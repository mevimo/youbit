#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The CLI of YouBit.
"""
from pathlib import Path
import os
from enum import Enum

import typer


app = typer.Typer(help="YouBit CLI", no_args_is_help=True, add_completion=False)
test_app = typer.Typer(no_args_is_help=True)
app.add_typer(test_app, name="test")


class BrowserChoice(str, Enum):
    CHROME = 'chromer'
    FIREFOX = 'firefox'
    OPERA = 'opera'
    EDGE = 'edge'
    CHROMIUM = 'chromium'
    BRAVE = 'brave'


class ResChoice(str, Enum):
    HD = 'HD'
    QHD = 'QHD'
    UHD = 'UHD'


ecc_option = typer.Option(
    32,
    help="Set the number of ECC symbols to use for FEC encoding. Set to 0 to disable ECC. Max 255.",
    min=0, max=255
)
res_option = typer.Option(
    'HD', help="Set the video resolution.",
    case_sensitive=False
)
bpp_option = typer.Option(
    1,
    help="The 'bpp' or 'Bits Per Pixel' value to use.",
    min=1, max=3
)
crf_option = typer.Option(
    18,
    help="The 'crf' or 'Constant Rate Factor' to use during video encoding.",
    min=0, max=52
)
nullframes_option = typer.Option(
    False,
    help="Whether or not to use nullframes. See the README.md for more information."
)


@app.command("encode", no_args_is_help=True)
def encode_local(
    input_path: Path = typer.Argument(..., help="A path to the file you wish to encode."),
    output_dir: Path = typer.Argument(
        Path(os.getcwd()), help="The directory in which to save the output."
    ),
    ecc: int = ecc_option,
    res: ResChoice = res_option,
    bpp: int = bpp_option,
    crf: int = crf_option,
    null_frames: bool = nullframes_option,
) -> None:
    from rich.console import Console
    from youbit import Encoder
    from youbit.settings import Settings, Resolution, BitsPerPixel

    settings = Settings(
        resolution=Resolution[res.upper()],
        bits_per_pixel=BitsPerPixel(bpp),
        ecc_symbols=ecc,
        constant_rate_factor=crf,
        null_frames=null_frames
    )
    encoder = Encoder(input_path, settings)

    console = Console()
    with console.status(f"Encoding '{str(input_path)}'...", spinner="bouncingBall"):
        output_path = encoder.encode_local(output_dir)
            
    console.rule(":green_circle:[bold green]Succes[/]:green_circle:")
    console.print(f"[green]File saved at: {output_path}.[/]")


@app.command("upload", no_args_is_help=True)
def encode_upload(
    input_path: Path = typer.Argument(..., help="A path to the file you wish to encode."),
    browser: BrowserChoice = typer.Argument(
        ...,
        help="Which browser to extract cookies "
        "from for upload. MAKE SURE this user has previously visited "
        "studio.youtube.com' and there are no more popops "
        "like 'choose channel name').",
        case_sensitive=False
    ),
    ecc: int = ecc_option,
    res: ResChoice = res_option,
    bpp: int = bpp_option,
    crf: int = crf_option,
    nullframes: bool = nullframes_option
) -> None:
    from rich.status import Status
    from rich.console import Console
    from youbit import Encoder
    from youbit.settings import Settings, BitsPerPixel, Browser, Resolution

    console = Console()
    status = Status(f"Uploading {input_path}...", spinner="bouncingBall")
    status.start()

    settings = Settings(
        resolution=Resolution[res.name],
        bits_per_pixel=BitsPerPixel(bpp),
        ecc_symbols=ecc,
        constant_rate_factor=crf,
        null_frames=nullframes,
        browser=Browser[browser.name]
    )
    encoder = Encoder(input_path, settings)
    url = encoder.encode_and_upload()

    status.stop()
    console.rule(":green_circle:[bold green]Succes[/]:green_circle:")
    console.print(f"[bold green]>>> [link={url}]{url}[/link] <<<[/]")


@app.command("decode", no_args_is_help=True)
def decode_local(
    input_path: Path = typer.Argument(..., help="A path to the file you wish to decode."),
    output_dir: Path = typer.Argument(
        Path(os.getcwd()), help="The directory in which to save the decoded file."
    ),
    metadata_str: str = typer.Argument(
        ...,
        help="The base64-encoded metadata string usually found in the video description."
    )
) -> None:
    from rich.console import Console
    from youbit import decode_local, Metadata

    console = Console()
    with console.status(f"Decoding '{str(input_path)}'...", spinner="bouncingBall"):
        metadata = Metadata.create_from_base64(metadata_str)
        output_path = decode_local(input_path, output_dir, metadata)

    console.rule(":green_circle:[bold green]Succes[/]:green_circle:")
    console.print(f"[green]File saved at: {str(output_path)}.[/]")


@app.command("download", no_args_is_help=True)
def decode_url(
    url: str = typer.Argument(
        ..., help="The YouTube URL of the video you wish to decode."
    ),
    output_dir: Path = typer.Argument(
        Path(os.getcwd()), help="The directory in which to save the file."
    )
) -> None:
    from rich.console import Console
    from youbit import download_and_decode

    console = Console()
    with console.status(f"Downloading video '{url}'...", spinner="bouncingBall"):
        output_path = download_and_decode(url, output_dir)
    
    console.rule(":green_circle:[bold green]Succes[/]:green_circle:")
    console.print(f"[green]File saved at: {output_path}.[/]")


# TEST APP COMMANDS
@test_app.command("vbr")
def test_vbr(url: str = typer.Argument(...)):
    """Prints the best available (usable) video bitrate for the given YouTube video."""
    from rich.console import Console
    from youbit import Downloader
    
    Console().print(
        Downloader(url).best_vbr
    )


@test_app.command("metadata")
def test_metadata(url: str = typer.Argument(...)):
    from rich.pretty import pprint
    from youbit import Downloader

    pprint(Downloader(url).youbit_metadata)


@test_app.command("compare")
def test_compare(file1: Path = typer.Argument(...), file2: Path = typer.Argument(...)):
    """Will compare binary information of two files, and print out the differences."""
    from youbit.util import compare_files
    from rich.pretty import pprint

    pprint(compare_files(file1, file2))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
