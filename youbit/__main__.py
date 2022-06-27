#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The CLI of YouBit.
"""
from pathlib import Path
from enum import Enum
import os

import typer


class Browser(str, Enum):
    """The possible browser to extract cookies from."""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    OPERA = "opera"
    BRAVE = "brave"
    CHROMIUM = "chromium"


app = typer.Typer(help="YouBit CLI", no_args_is_help=True, add_completion=False)
encode_app = typer.Typer(no_args_is_help=True)
app.add_typer(encode_app, name="encode")
decode_app = typer.Typer(no_args_is_help=True)
app.add_typer(decode_app, name="decode")
test_app = typer.Typer(no_args_is_help=True)
app.add_typer(test_app, name="test")


opt_encode_ecc = typer.Option(
    32,
    help="Set the number of ECC symbols to use for FEC encoding. Set to 0 to disable ECC. Max 255.",
)
opt_encode_res = typer.Option(
    "hd", help="Set the video resolution. Can be 'hd', '2k', '4k' or '8k'."
)
opt_encode_bpp = typer.Option(
    1,
    help="The 'bpp' or 'Bits Per Pixel' value to use."
        "Determines how many bits to store in each pixel of the video. 1, 2 or 3.",
)
opt_encode_crf = typer.Option(
    18,
    help="The 'crf' or 'Constant Rate Factor' to use during video encoding. 0 - 52 inclusive.",
)
opt_upload_title = typer.Option(
    None,
    help="The title for the YouTube video. Defaults to the filename.",
    show_default=False,
)
opt_encode_zero_frame = typer.Option(
    False,
    help="Whether or not to use a zeroframes. See the README.md for more information.",
)
opt_headless = typer.Option(
    True,
    help="Whether or not to run the selenium browser in headless mode during upload.",
)


@test_app.command("vbr")
def test_vbr(url: str = typer.Argument(...)):
    """Prints the best available video bitrate for the given YouTube video."""
    from rich.console import Console
    from youbit import Decoder
    
    console = Console()
    with Decoder(url) as decoder:
        vbr = decoder.downloader.best_vbr
        if decoder.metadata.get("zero_frame"):
            good_vbr = None
        else:
            if decoder.metadata.get("resolution") == (1920, 1080):
                good_vbr = 10000
            elif decoder.metadata.get("resolution") == (2560, 1440):
                good_vbr = 19500
            elif decoder.metadata.get("resolution") == (3840, 2160):
                good_vbr = 47500
            elif decoder.metadata.get("resolution") == (7680, 4320):
                good_vbr = 172000
    if good_vbr:
        if vbr > good_vbr:
            color = "green"
        else:
            color = "red"
        console.print(f"[{color}]{vbr}[/]")
    else:
        console.print(f"[yellow]{vbr}[/]")
        console.print("[yellow]This video uses zero frames: may or may not work.[/]")


@test_app.command("metadata")
def test_metadata(url: str = typer.Argument(...)):
    from rich.pretty import pprint
    from youbit import Decoder

    with Decoder(url) as decoder:
        for k, v in decoder.metadata.items():
            print(k, end=": ")
            pprint(v)


@test_app.command("compare")
def test_compare(file1: Path = typer.Argument(...), file2: Path = typer.Argument(...)):
    """Will compare binary information of two files, and print out the differences."""
    from youbit.util import compare_files
    from rich.pretty import pprint

    result = compare_files(file1, file2)
    for k, v in result.items():
        print(k, end=": ")
        pprint(v)


@encode_app.command("local", no_args_is_help=True)
def encode_local(
    input: Path = typer.Argument(..., help="A path to the file you wish to encode."),
    output: Path = typer.Argument(
        Path(os.getcwd()), help="The directory in which to save the output."
    ),
    ecc: int = opt_encode_ecc,
    res: str = opt_encode_res,
    bpp: int = opt_encode_bpp,
    crf: int = opt_encode_crf,
    zero_frame: bool = opt_encode_zero_frame,
) -> None:
    from rich.console import Console
    from youbit import Encoder

    console = Console()
    with console.status(f"Encoding '{str(input)}'...", spinner="bouncingBall"):
        with Encoder(input) as encoder:
            path = encoder.encode(
                directory=output,
                ecc=ecc,
                bpp=bpp,
                crf=crf,
                res=res,
                zero_frame=zero_frame,
            )
    console.rule(":green_circle:[bold green]Succes[/]:green_circle:")
    console.print(f"[green]File saved at: {path}.[/]")


@encode_app.command("upload", no_args_is_help=True)
def encode_upload(
    input: Path = typer.Argument(..., help="A path to the file you wish to encode."),
    browser: Browser = typer.Argument(
        ...,
        help="Which browser to extract the currently logged-in user (YouTube)"
        "from for upload. MAKE SURE this user has previously visited"
        "studio.youtube.com' and there are no more popops"
        "like 'choose channel name').",
        case_sensitive=False,
    ),
    video_title: str = opt_upload_title,
    ecc: int = opt_encode_ecc,
    res: str = opt_encode_res,
    bpp: int = opt_encode_bpp,
    crf: int = opt_encode_crf,
    zero_frame: bool = opt_encode_zero_frame,
    headless: bool = opt_headless,
) -> None:
    from rich.status import Status
    from rich.console import Console
    from youbit import Encoder

    console = Console()
    status = Status(f"Encoding {input}...", spinner="bouncingBall")
    status.start()
    with Encoder(input) as encoder:
        encoder.encode(ecc=ecc, bpp=bpp, crf=crf, res=res, zero_frame=zero_frame)
        status.update("Uploading...", spinner="bouncingBall")
        url = encoder.upload(
            title=video_title, browser=browser.value, headless=headless
        )
    status.stop()
    console.rule(":green_circle:[bold green]Succes[/]:green_circle:")
    console.print(f"[bold green]>>> [link={url}]{url}[/link] <<<[/]")


@decode_app.command("local", no_args_is_help=True)
def decode_local(
    input: Path = typer.Argument(..., help="A path to the file you wish to decode."),
    output: Path = typer.Argument(
        Path(os.getcwd()), help="A path to where you want to save the decoded file."
    ),
    ecc: int = typer.Argument(
        ..., help="The number of ECC symbols that were used during encoding."
    ),
    bpp: int = typer.Argument(
        ..., help="The 'bpp' or 'Bits Per Pixel' value that was used during encoding."
    ),
    zero_frame: bool = typer.Argument(
        ..., help="Whether ot not a 'zeroframe' was used during encoding."
    ),
) -> None:
    from rich.console import Console
    from youbit import Decoder

    console = Console()
    with console.status(f"Decoding '{str(input)}'...", spinner="bouncingBall"):
        with Decoder(input) as decoder:
            decoder.decode(output=output, ecc=ecc, bpp=bpp, zero_frame=zero_frame)
    console.rule(":green_circle:[bold green]Succes[/]:green_circle:")
    console.print(f"[green]File saved at: {str(output)}.[/]")


@decode_app.command("url", no_args_is_help=True)
def decode_url(
    input: str = typer.Argument(
        ..., help="The YouTube URL of the video you wish to decode."
    ),
    output: Path = typer.Argument(
        Path(os.getcwd()), help="The directory in which to save the file."
    ),
) -> None:
    from rich.status import Status
    from rich.console import Console
    from youbit import Decoder

    console = Console()
    status = Status(f"Downloading video...", spinner="bouncingBall")
    status.start()
    with Decoder(input) as decoder:
        decoder.download()
        status.update(f"Decoding...", spinner="bouncingBall")
        filepath = decoder.decode(output)
    status.stop()
    console.rule(":green_circle:[bold green]Succes[/]:green_circle:")
    console.print(f"[green]File saved at: {filepath}.[/]")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
