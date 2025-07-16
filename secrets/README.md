# Loading API Keys Into Codebase

The following API keys are required to run the application:
- GEMINI_API_KEY
- CLAUDE_API_KEY
- LANGSMITH_API_KEY
- GITHUB_PA_TOKEN

## How to store API keys on your system

Once you have acquired these keys from the listed providers, rename the `.env.example` file to 
`.env` and paste your keys into it at their corresponding names.

## How to load the API keys into your code

A loader script is located in `secrets/secrets_loader.py`. To load a token, import the package into
your script and call the function `SecretsLoader.get_token("[NAME OF TOKEN]", "[.env FILEPATH]")`.

**NOTE**: the default filepath is already set to the location of the `.env` file. Only change it if
you have rellocated your `.env` file. 