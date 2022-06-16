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


opt_encode_ecc = typer.Option(32, help="Set the number of ECC symbols to use for FEC encoding. Set to 0 to disable ECC. Max 255.")
opt_encode_res = typer.Option("1920x1080", help="Set the video resolution.")
opt_encode_bpp = typer.Option(1, help="The 'bpp' or 'Bits Per Pixel' value to use. Determines how many bits to store in each pixel of the video. 1, 2 or 3.")
opt_encode_crf = typer.Option(18, help="The 'crf' or 'Constant Rate Factor' to use during video encoding. 0 - 52 inclusive.")
opt_overwrite = typer.Option(False, help="Whether or not to allow overwriting other files.")


CONSOLE = Console()


@encode_app.command("local", no_args_is_help=True)
def encode_local(
    input: Path = typer.Argument(..., help="A path to the file you wish to encode."),
    output: Path = typer.Argument(
        ..., help="A path to where you want to save the encoded file."
    ),
    ecc: int = opt_encode_ecc,
    res: str = opt_encode_res,
    bpp: int = opt_encode_bpp,
    crf: int = opt_encode_crf,
    overwrite: bool = opt_overwrite
):
    with CONSOLE.status(f"Encoding '{str(input)}'...", spinner='bouncingBall'):
        res = tuple(map(int, res.split('x')))
        with Encoder(input) as encoder:
            encoder.encode(
                path=output,
                overwrite=overwrite,
                ecc=ecc,
                bpp=bpp,
                crf=crf,
                res=res
            )
    CONSOLE.rule(":green_circle:[bold green]Succes[/]:green_circle:")
    CONSOLE.print(f"[green]Video saved at: {str(output)}.[/]") 


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
    video_title: str = typer.Argument(..., help="The title to use for the uploaded YouTube video."),
    ecc: int = opt_encode_ecc,
    res: str = opt_encode_res,
    bpp: int = opt_encode_bpp,
    crf: int = opt_encode_crf
):
    status = Status(f'Encoding {input}...', spinner='bouncingBall')
    status.start()
    with Encoder(input) as encoder:
        res = tuple(map(int, res.split('x')))
        encoder.encode(
            ecc=ecc,
            bpp=bpp,
            crf=crf,
            res=res
        )
        status.update("Uploading...", spinner="bouncingBall")
        url = encoder.upload(title=video_title, browser=browser.value)
    status.stop()
    CONSOLE.rule(":green_circle:[bold green]Succes[/]:green_circle:")
    CONSOLE.print(f"[bold green]>>> [link={url}]{url}[/link] <<<[/]")


@decode_app.command("local", no_args_is_help=True)
def decode_local(
    input: Path = typer.Argument(..., help="A path to the file you wish to decode."),
    output: Path = typer.Argument(
        ..., help="A path to where you want to save the decoded file."
    ),
    ecc: int = typer.Argument(..., help="The number of ECC symbols that were used during encoding."),
    bpp: int = typer.Argument(..., help="The 'bpp' or 'Bits Per Pixel' value that was used during encoding."),
    overwrite: bool = opt_overwrite
):
    with CONSOLE.status(f"Decoding '{str(input)}'...", spinner='bouncingBall'):
        with Decoder(input) as decoder:
            decoder.decode(
                output=output,
                overwrite=overwrite,

            )
    CONSOLE.rule(":green_circle:[bold green]Succes[/]:green_circle:")
    CONSOLE.print(f"[green]File saved at: {str(output)}.[/]")


@decode_app.command("url", no_args_is_help=True)
def decode_url(
    input: str = typer.Argument(
        ..., help="The YouTube URL of the video you wish to decode."
    ),
    output: Path = typer.Argument(
        ..., help="A path to where you want to save the decoded file."
    ),
    overwrite: bool = opt_overwrite
):
    status = Status(f'Downloading video...', spinner='bouncingBall')
    status.start()
    with Decoder(input) as decoder:
        decoder.download()
        status.update(f"Decoding...", spinner='bouncingBall')
        decoder.decode(output=output, overwrite=overwrite)
    status.stop()
    CONSOLE.rule(":green_circle:[bold green]Succes[/]:green_circle:")
    CONSOLE.print(f"[green]File saved at: {str(output)}.[/]")


if __name__ == "__main__":
    app()
