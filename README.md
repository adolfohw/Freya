# Freya Discord Bot

## Installation

### Using a virtual environment (optional)

On Windows, use ``python`` or ``py`` instead.

```sh
python3 -m venv freya-env
```

Then, activate it; for Windows cmd:

```cmd
freya-env\Scripts\activate.bat
```

For Windows PowerShell:

```ps
freya-env\Scripts\Activate.ps1
```

For other OSes:

```sh
source freya-env/bin/activate (Other)
```

### Dependencies

Installing python packages required:

```sh
pip install -r requirements.txt
```

Creating a secret file with the bot's token:

```sh
echo "TOKEN = 'token here'" > secret.py
```