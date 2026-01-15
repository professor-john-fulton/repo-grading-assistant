## Quickstart.md


> If you haven’t installed yet, see README → Installation.


1) You will need an OpeanAI paid account to run this project, except for pytest suite and --help and --dry-run

2) Generate an API key and put it somewhere safe. This should help: https://platform.openai.com/docs/quickstart  Setup the key to have access to the gpt-5 model.

3) The key should be a project key string of the form "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" (this isn't a real key). Put the key in a .env file at the top level of the project.
```
OPENAI_API_KEY="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" 
```



You may create a ./keys/ directory  at the base level. Use ./docs/examples/grading_key_example.txt to create an example key file

In the ./configs/ directory, you should create  ./docs/examples/grading_config_example.json to create an example config file



🔒 Critical rules (put in bold in docs)

DO NOT rename the project folder after creating .venv

Always use python -m pip, not pip

Activate venv every session

Recovery section (short but powerful)

If you renamed/moved the folder:

deactivate
rm -rf .venv
python -m venv .venv
source .venv/Scripts/activate   # or bin/activate
python -m pip install -e .

Optional verification
which python
python -c "import sys; print(sys.executable)"
repo-grading-assistant --help

Why this matters (1-liner)

Editable installs hard-code absolute paths.
Renaming breaks launchers.

Mentor suggestion

Add a "Common Errors" section with:

Fatal error in launcher

PATH conflicts

Multiple Python installs