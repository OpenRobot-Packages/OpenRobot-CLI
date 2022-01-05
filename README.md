# OpenRobot-CLI
A CLI/Shell supporting [JeyyAPI](https://api.jeyy,xyz), [OpenRobot API](https://api.openrobot.xyz) and [RePI API](https://repi.openrobot.xyz).

# Installation:
```sh
pip install -U git+https://github.com/OpenRobot-Packages/OpenRobot-CLI
```

# Commands:
```
┌── openrobot: Opens the OpenRobot CLI
|   ├── api: Manages OpenRobot API
|   |   ├── configure: Configures the OpenRobot API cridentials to authenticate to the API
|   |   ├── config: An alias of configure command
|   |   ├── lyrics <query> [--format json|text]: Gets/Searches lyrics from a query. This access the /api/lyrics endpoint.
|   |   ├── nsfw-check <url> [--format json|text]: Performs a NSFW Check using the /api/nsfw-check endpoint.
|   |   ├── celebrity <url> [--format json|text]: Performs a Celebrity Detection using the /api/celebrity endpoint.
│   ├── jeyy: Manages Jeyy API
│   ├── repi: Manages RePI API
```