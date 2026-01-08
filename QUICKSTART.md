## Quickstart.md

This is the place to start.

1) You will need an OpeanAI paid account to run this project.

2) Generate an API key and put it somewhere safe. This should help: https://platform.openai.com/docs/quickstart  Setup the key to have access to the gpt-5 model.

3) The key should be a project key string of the form "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" (this isn't a real key). Put the key in the .env file at the top level of the project.
```
OPENAI_API_KEY="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" 
```

4) Python runs best inside of a virtual environment. Other enviroments should work but venv is built into python
    - py -3.11 -m venv .venv
    - source .venv/Scripts/activate
    - python -m pip install -U pip setuptools wheel

    - pip install -r requirements.txt 
