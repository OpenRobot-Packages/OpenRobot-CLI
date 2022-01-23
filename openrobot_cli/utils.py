import click

def blue_text(text):
    return click.style(text, fg="blue")

def error(text):
    return click.style(text, fg="red")