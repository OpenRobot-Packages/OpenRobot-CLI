import os
import sys
import json
import click
import typing
import requests

from tabulate import tabulate

from ..utils import blue_text, error

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
        token = os.environ.get('OPENROBOT_API_TOKEN')

    token = token or 'I-Am-Testing' # Just in case if the token key in the JSON file is falsely a.k.a None, empty string, etc.

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
@main.group("text-generation", invoke_without_command=True)
@click.argument("text", default=None, nargs=-1, type=str, required=True)
@click.option("--max-length", "max_length", is_flag=True, default=None, type=int, help="The maximum length of the generated text. Defaults to None.")
@click.option("--num-return", "num_return", is_flag=True, default=None, type=int, help="The number of generated texts to return. Defaults to 1.")
@click.option("--format", default="text", is_flag=True, type=click.Choice(["json", "text"]), help="Output format. Text will be an output with Title, Artist and Lyrics. JSON will be a JSON object returned by the API.")
@click.pass_context
def text_generation(ctx: click.Context, text: str, max_length: int, num_return: int, format: str):
    """
    Text Generation/Completion. This uses the /api/text-generation endpoint.
    """

    if 'get' in sys.argv: # Click doesn't work well for some reason.
        try:
            task_id = sys.argv[sys.argv.index('get') + 1]
        except:
            task_id = None

        print(task_id)

        ctx.invoke(text_generation_get, format=format, task_id=task_id)

    if ctx.invoked_subcommand is None:
        if text:
            text = ' '.join(text)

            js = client.text_generation(text, max_length=max_length, num_return=num_return).raw

            if format == "json":
                click.echo(js)
            else:
                s = "\n".join(f'{k}: {v}' for k, v in js.items())

                click.echo(s)

            ctx.exit()

        help_str = ctx.get_help()
        click.echo(help_str)

        ctx.exit()

@text_generation.command("get")
@click.argument("task_id", type=str)
@click.option("--format", default="text", type=click.Choice(["json", "text"]), help="Output format. Text will be an output with Title, Artist and Lyrics. JSON will be a JSON object returned by the API.")
@click.pass_context
def text_generation_get(ctx: click.Context, task_id: str, format: str):
    """
    Get a text generation task.
    """

    js = client.text_generation_get(task_id).raw

    if format == "json":
        click.echo(js)
    else:
        s = "\n".join(f'{k}: {v}' for k, v in js.items())

        click.echo(s)

    ctx.exit()

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

@main.group("text-to-speech", invoke_without_command=True)
@click.argument("text", type=str, nargs=-1)
@click.option("--save-to", "-st", "--st", "save_to", default=None, type=str, help="Save the audio to a file.")
@click.option("--language", "-l", "languagge", default="en-US", type=str, help="Language Code to use for the TTS. Default is en-US.")
@click.option("--voice", "-v", "voice", default=None, type=str, help="Voice ID to use. Default is the first voice returned by the API according to the language.")
@click.pass_context
def text_to_speech(ctx: click.Context, text: str, save_to: str, language: str, voice: str):
    """
    Performs a Text-To-Speech using the /api/text-to-speech endpoint.
    """

    if 'support' in sys.argv: # Click doesn't work well for some reason.
        try:
            language = sys.argv[sys.argv.index('support') + 1]
        except:
            language = None

        ctx.invoke(text_to_speech_support, language=language)

    if ctx.invoked_subcommand is None:
        print(language)
        print(voice)
        if voice is None:
            voices = client.speech.text_to_speech_support(language).voices

            print(voices)

            if not voices:
                click.echo(error("Error:") + " No voices available for the specified language.")
                ctx.exit(1)

            voice = voices[0].id

        audio = client.speech.text_to_speech(text, language, voice)

        print(save_to)

        if save_to:
            r = requests.get(audio.url)

            audio_bytes = r.content

            with open(save_to, "wb") as f:
                f.write(audio_bytes)

            click.echo(f"Audio saved to {blue_text(save_to)}.")
        else:
            click.echo(blue_text('URL:') + ' ' + audio.url)

        ctx.exit()

@text_to_speech.command("support")
@click.argument("language", type=str, default=None)
@click.pass_context
def text_to_speech_support(ctx: click.Context, language: str):
    """
    Lists the available languages and voices for the specified language.
    """

    if language is None:
        languages = client._request(
            "GET",
            "/api/speech/text-to-speech/supports",
            params={"engine": "standard"},
        )

        languages = [[x] for x in languages['languages']]

        for language in languages:
            language_name = client.speech.text_to_speech_support(language).voices

            if language_name:
                language.append(language_name[0].language.name)
            else:
                language.append("Unknown")

        click.echo(blue_text("Text to Speech Supported Languages:") + "\n\n" + tabulate(languages, headers=["Code", "Name"], tablefmt="fancy_grid"))
    else:
        voices = client.speech.text_to_speech_support(language).voices

        s = f"{click.style(f'Voices supported for Language {voices[0].language.name}:', fg='bright_cyan')}\n\n"

        for voice in voices:
            s += click.style("#" + str(voices.index(voice) + 1), fg='bright_cyan') + "\n"

            s += f"{blue_text('Name:')} {voice.name}\n"
            s += f"{blue_text('Gender:')} {voice.gender}\n"
            s += f"{blue_text('Voice ID:')} {voice.id}\n"

            s += "\n"

        click.echo(s)

    ctx.exit()

@main.group("speech-to-text", invoke_without_command=True)
@click.argument("language", type=str, default="en-US")
@click.argument("file", default=None, type=str, nargs=-1)
@click.pass_context
def speech_to_text(ctx: click.Context, language: str, file: str):
    """
    Performs a Speech-To-Text using the /api/speech-to-text endpoint.
    """

    file = ' '.join(file)

    if 'support' in sys.argv:
        ctx.invoke(speech_to_text_support)

    if ctx.invoked_subcommand is None:
        languages = client.speech.speech_to_text_support()['languages']

        if language not in languages:
            click.echo(error("Error:") + " Language not found or not supported.")
            ctx.exit(1)

        audio = client.speech.speech_to_text(file, language)

        click.echo(blue_text("Time taken:") + " " + str(audio.duration))
        click.echo(blue_text("Transcription:") + "\n" + audio.text or click.style("No transcription found.", fg='red'))

        ctx.exit()

@speech_to_text.command("support")
@click.pass_context
def speech_to_text_support(ctx: click.Context):
    """
    Lists the available languages for the Speech-To-Text endpoint.
    """

    languages = client.speech.speech_to_text_support()['languages']

    x = "- " + "\n- ".join([x for x in languages])

    click.echo(blue_text("Speech to Text Supported Languages:") + "\n\n" + (x if x else 'None.'))

    ctx.exit()

def api_cli_setup(cmd: click.Group):
    cmd.add_command(main)