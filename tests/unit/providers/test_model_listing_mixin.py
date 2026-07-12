import pytest

from textfsm_ai.providers.model_listing_mixin import ModelListingMixin


class _FakeListingProvider(ModelListingMixin):
    name = "openai"

    def __init__(self, models):
        self._models = models

    def fetch_latest_models(self):
        return self._models


# ============================================================
# list_models_curated
# ============================================================


def test_list_models_curated_returns_real_openai_groups():
    class _OpenAI(ModelListingMixin):
        name = "openai"

    groups = _OpenAI.list_models_curated()

    assert "quality-chat" in groups
    assert isinstance(groups["quality-chat"], list)


def test_list_models_curated_missing_file_raises(tmp_path, monkeypatch):
    class _Fake(ModelListingMixin):
        name = "openai"
        CURATED_PATH = tmp_path / "does-not-exist.yaml"

    with pytest.raises(FileNotFoundError):
        _Fake.list_models_curated()


def test_list_models_curated_unknown_provider_raises(tmp_path):
    yaml_file = tmp_path / "curated.yaml"
    yaml_file.write_text("openai:\n  quality-chat: []\n", encoding="utf-8")

    class _Unknown(ModelListingMixin):
        name = "not-a-real-provider"
        CURATED_PATH = yaml_file

    with pytest.raises(KeyError):
        _Unknown.list_models_curated()


def test_list_models_curated_empty_file_raises_keyerror(tmp_path):
    yaml_file = tmp_path / "empty.yaml"
    yaml_file.write_text("", encoding="utf-8")

    class _Fake(ModelListingMixin):
        name = "openai"
        CURATED_PATH = yaml_file

    with pytest.raises(KeyError):
        _Fake.list_models_curated()


# ============================================================
# fetch_latest_models (base implementation)
# ============================================================


def test_fetch_latest_models_base_raises_not_implemented():
    class _Bare(ModelListingMixin):
        name = "bare"

    with pytest.raises(NotImplementedError):
        _Bare().fetch_latest_models()


# ============================================================
# classify_models
# ============================================================


def test_classify_models_delegates_to_fetch_and_classifier():
    provider = _FakeListingProvider(["gpt-4o", "gpt-4o-mini"])
    groups = provider.classify_models()

    # classify_models() routes "openai" through classify_openai_models;
    # just confirm it returns tier-group shaped data derived from our fakes.
    all_models = [m for models in groups.values() for m in models]
    assert "gpt-4o" in all_models
    assert "gpt-4o-mini" in all_models


def test_classify_models_empty_list_returns_empty_groups():
    provider = _FakeListingProvider([])
    groups = provider.classify_models()

    all_models = [m for models in groups.values() for m in models]
    assert all_models == []
