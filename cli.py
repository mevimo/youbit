from pathlib import Path
from enum import Enum
from time import sleep

import typer
from rich.status import Status
from rich.console import Console

from youbit import Encoder, Decoder


class Browser(str, Enum):
    chrome = "chrome"
    firefox = "firefox"
    edge = "edge"
    opera = "opera"
    brave = "brave"
    chromium = "chromium"


app = typer.Typer(help="YouBit CLI", no_args_is_help=True, add_completion=False)
encode_app = typer.Typer(no_args_is_help=True)
app.add_typer(encode_app, name="encode")
decode_app = typer.Typer(no_args_is_help=True)
app.add_typer(decode_app, name="decode")


@encode_app.command("local", no_args_is_help=True)
def encode_local(
    input: Path = typer.Argument(..., help="A path to the file you wish to encode."),
    output: Path = typer.Argument(
        ..., help="A path to where you want to save the encoded file."
    ),
):
    pass


@encode_app.command("upload", no_args_is_help=True)
def encode_upload(
    input: Path = typer.Argument(..., help="A path to the file you wish to encode."),
    output: Browser = typer.Argument(
        ...,
        help="Which browser to extract the currently logged-in user (YouTube)"
            "from for upload. MAKE SURE this user has previously visited"
            "studio.youtube.com' and there are no more popops"
            "like 'choose channel name').",
        case_sensitive=False,
    ),
):
    status = Status('Encoding...', spinner='bouncingBall')
    status.start()
    
    sleep(5)
    status.update('Uploading...')
    sleep(5)
    status.stop()
    # with Encoder(input) as encoder:
    #     encoder.encode()
    #     encoder.upload()


@decode_app.command("local", no_args_is_help=True)
def decode_local(
    input: Path = typer.Argument(..., help="A path to the file you wish to decode."),
    output: Path = typer.Argument(
        ..., help="A path to where you want to save the decoded file."
    ),
):
    pass


@decode_app.command("url", no_args_is_help=True)
def decode_url(
    input: str = typer.Argument(
        ..., help="The YouTube URL of the video you wish to decode."
    ),
    output: Path = typer.Argument(
        ..., help="A path to where you want to save the decoded file."
    ),
):
    pass


if __name__ == "__main__":
    console = Console()
    app()
