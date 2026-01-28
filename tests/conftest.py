# tests/conftest.py

import json
import pytest
import logging

@pytest.fixture(scope="session", autouse=True)
def test_run_logger():
    """Logs the start and end of the test session."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s:%(lineno)d %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler("tests/test_run.log", mode="a", encoding="utf-8"),
            logging.StreamHandler()
        ],
    )
    logger = logging.getLogger(__name__)
    logger.info("=== Test session started ===")
    print("\n[pytest] Logging test output to tests/test_run.log\n")
    yield
    logger.info("=== Test session finished ===")


@pytest.fixture
def temp_project(tmp_path):
    """Creates a fake homework folder with a config, logs, and a dummy key."""
    root = tmp_path / "Homework06"
    root.mkdir()

    logs_dir = root / "logs"
    logs_dir.mkdir()

    configs_dir = root / "configs"
    configs_dir.mkdir()


    # New default behavior: prompt file lives next to the config file
    system_prompt_file = configs_dir / "base_system_prompt.txt"
    system_prompt_file.write_text("You are grading.", encoding="utf-8")

    # (Optional) keep prompts/ folder if other tests need it
    prompts_dir = root / "prompts"
    prompts_dir.mkdir()


    config_file = configs_dir / "homework6_config.json"
    config_file.write_text(json.dumps({
        "assignment_name": "Homework 6",
        "points_possible": 100,
        "rubric_path": "rubric.txt",
        "grading_key_file": "../keys/key.txt",
        "required_files": ["main.py", "readme.txt"],
        "model": "gpt-5-mini"
    }))

    student_dir = root / "homework-student_jdoe"
    student_dir.mkdir()
    (student_dir / "main.py").write_text("print('Hello world')")
    (student_dir / "readme.txt").write_text("John Doe submission")

    fake_key = root / "fake_key.json"
    fake_key.write_text("{}")

    # create keys/ folder and a fake key file
    keys_dir = root / "keys"
    keys_dir.mkdir(parents=True, exist_ok=True)

    grading_key_file = keys_dir / "key.txt"
    grading_key_file.write_text("Answer key content", encoding="utf-8")

    return {
        "root": root,
        "logs": logs_dir,
        "configs": configs_dir,
        "prompts": prompts_dir,
        "system_prompt_file": system_prompt_file,
        "config_file": config_file,
        "student_dir": student_dir,
        "grading_key_file": grading_key_file,
    }


@pytest.fixture
def fake_env(monkeypatch):
    """Sets a fake OPENAI_API_KEY environment variable."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    yield
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


@pytest.fixture
def fake_openai(monkeypatch):
    """Mocks openai.ChatCompletion.create to return fake grading output."""
    class FakeResponse:
        choices = [type("obj", (), {
            "message": {"content": "Grading complete.\nScore: 90/100\n- Missing comments (-10 points)"}
        })]
    def mock_create(*args, **kwargs):
        return FakeResponse()
    monkeypatch.setattr("openai.ChatCompletion.create", mock_create)


@pytest.fixture
def sample_log(caplog):
    """Captures log output during tests."""
    caplog.set_level("INFO")
    return caplog
