from pathlib import Path

from face_replace.config import load_config


def test_config_selects_provider_and_model(tmp_path: Path) -> None:
    path = tmp_path / "config.yaml"
    path.write_text(
        "runtime:\n"
        "  provider: test-provider\n"
        "  model: test-model\n"
        "  device: cuda\n"
        "  models_dir: cache\n"
    )

    config = load_config(path)

    assert config.runtime.provider == "test-provider"
    assert config.runtime.model == "test-model"
    assert config.runtime.models_dir == (tmp_path / "cache").resolve()
