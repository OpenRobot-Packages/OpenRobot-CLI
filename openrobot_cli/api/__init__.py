import os
import json
import click

from ..utils import blue_text

from openrobot.api_wrapper import SyncClient

def get_token():
    try:
        dir = os.path.expanduser("~/.openrobot")

        with open(f'{dir}/api/cridentials.json', 'r') as f:
            cridentials = json.load(f)

            token = cridentials['token']
    except:
        token = None

    return token

def setup_client():
    try:
        dir = os.path.expanduser("~/.openrobot")

        with open(f'{dir}/api/cridentials.json', 'r') as f:
            cridentials = json.load(f)

            token = cridentials['token']
    except:
        token = os.environ.get('OPENROBOT_API_TOKEN') or 'I-Am-Testing'

    global client
    client = SyncClient(token, ignore_warning=True)

setup_client()

@click.group("api", invoke_without_command=True)
@click.pass_context
def main(ctx: click.Context):
    """
    OpenRobot API. You can configure and use the OpenRobot API.
    """

    if ctx.invoked_subcommand is None:
        help_str = ctx.get_help()
        click.echo(help_str)

        ctx.exit()

@main.command("configure")
@click.option('--token', prompt=blue_text('Please enter your API Token ') + '[' + (get_token() or "I-Am-Testing") + ']', default=None)
@click.pass_context
def configure(ctx: click.Context, token: str):
    """
    Configure OpenRobot API.
    """

    token = token or get_token() or 'I-Am-Testing'

    dir = os.path.expanduser("~/.openrobot")

    try:
        os.mkdir(dir)
    except FileExistsError:
        pass

    try:
        os.mkdir(f'{dir}/api')
    except FileExistsError:
        pass

    with open(f'{dir}/api/cridentials.json', 'w') as fp:
        json.dump({'token': token}, fp)

    setup_client()

    click.echo(f'OpenRobot API configured successfully!')

    ctx.exit()

@main.command("config")
@click.option('--token', prompt=blue_text('Please enter your API Token ') + '[' + (get_token() or "I-Am-Testing") + ']', default=None, help="The token to use to authenticate to APIs.")
@click.pass_context
def configure(ctx: click.Context, token: str):
    """An alias of configure command."""
    ctx.invoke(configure, token=token)

# API commands
@main.command("lyrics")
@click.argument("query", nargs=-1, type=str)
@click.option("--format", default="text", type=click.Choice(["json", "text"]), help="Output format. Text will be an output with Title, Artist and Lyrics. JSON will be a JSON object returned by the API.")
@click.pass_context
def lyrics(ctx: click.Context, query: str, format: str):
    """
    Gets/Searches lyrics from a query. This access the /api/lyrics endpoint.
    """

    query = ' '.join(query)

    lyrics = client.lyrics(query)

    if format == "json":
        click.echo(json.dumps(lyrics.raw))
    else:
        if lyrics.lyrics is None:
            click.echo(f"No lyrics found for {query}")
            ctx.exit()

        s = f"""{blue_text("Title:")} {lyrics.title or "Unknown."}
{blue_text("Artist:")} {lyrics.artist or "Unknown."}

{lyrics.lyrics}"""

        click.echo(s)

    ctx.exit()

@main.command("nsfw-check")
@click.argument("url", type=str)
@click.option("--format", default="text", type=click.Choice(["json", "text"]), help="Output format. Text will be an output with Safe/Unsafe score and Labels. JSON will be a JSON object returned by the API.")
@click.pass_context
def nsfw_check(ctx: click.Context, url: str, format: str):
    """
    Performs a NSFW Check using the /api/nsfw-check endpoint.
    """

    nsfw = client.nsfw_check(url)

    if format == "json":
        click.echo(json.dumps(nsfw.raw))
    else:
        safe_score = 100 - nsfw.score * 100
        unsafe_score = nsfw.score * 100

        is_safe = not bool(nsfw.labels) and safe_score > unsafe_score

        s = f"""{click.style("Safe Score:", fg="green")} {round(safe_score, 1)}%
{click.style("Unsafe Score:", fg="red")} {round(unsafe_score, 1)}%

{click.style("Is Safe:", fg="green" if is_safe else "red")} {is_safe}

{blue_text("Labels:")}"""

        parent_name_added = []

        if nsfw.labels:
            for label in reversed(nsfw.labels):
                if label.name in parent_name_added:
                    continue

                s += f'\n- {label.name} - Confidence: {round(label.confidence, 1)}%'

                if label.parent_name:
                    parent_name_added.append(label.parent_name)
        else:
            s += f' None'

        click.echo(s)

    ctx.exit()

@main.command("celebrity")
@click.argument("url", type=str)
@click.option("--format", default="text", type=click.Choice(["json", "text"]), help="Output format. Text will be an output with the details of the detected celebrity. JSON will be a JSON object returned by the API.")
@click.pass_context
def celebrity(ctx: click.Context, url: str, format: str):
    """
    Performs a Celebrity Detection using the /api/celebrity endpoint.
    """

    detected = client.celebrity(url)

    if format == "json":
        click.echo(json.dumps([x.raw for x in detected] or {"detectedFaces": []}))
    else:
        if not detected:
            click.echo(f"No celebrity detected.")
            ctx.exit()
            
        for celebrity in detected:
            newline = "\n"

            s = ""

            if len(detected) > 1:
                s += click.style("#" + str(detected.index(celebrity) + 1), fg="bright_cyan")

            s += f"""
{blue_text("Name:")} {celebrity.name}
{blue_text("Gender:")} {celebrity.gender}
{blue_text("Confidence:")} {round(celebrity.confidence, 1)}%
{blue_text("URLs:")}{f"{newline}- " + f"{newline}- ".join(celebrity.urls) if celebrity.urls else " None"}
{blue_text("Face:")}
    - {blue_text("Pose:")}
        - {blue_text("Roll:")} {celebrity.face.pose.roll}
        - {blue_text("Yaw:")} {celebrity.face.pose.yaw}
        - {blue_text("Pitch:")} {celebrity.face.pose.pitch}
    - {blue_text("Quality:")}
        - {blue_text("Brightness:")} {celebrity.face.quality.brightness}
        - {blue_text("Sharpness:")} {celebrity.face.quality.sharpness}
    - {blue_text("Emotions:")}{f"{newline}        - " + f"{newline}        - ".join([f'{emotion.type.lower().capitalize()} - Confidence: {round(emotion.confidence, 1)}%' for emotion in sorted(celebrity.face.emotions, key=lambda i: i.confidence, reverse=True)]) if celebrity.face.emotions else " Unknown."}
    - {blue_text("Is Smiling:")} {celebrity.face.smile.value} - Confidence: {round(celebrity.face.smile.confidence, 1)}%"""

            if detected.index(celebrity) + 1 < len(detected):
                s += "\n"

            click.echo(s)

    ctx.exit()

def api_cli_setup(cmd: click.Group):
    cmd.add_command(main)