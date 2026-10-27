from engine import voice_registry


def registry_in_tmp_path(monkeypatch, tmp_path):
    monkeypatch.setattr(voice_registry, 'DATA_DIR', tmp_path / 'data')
    monkeypatch.setattr(voice_registry, 'CONFIG_FILE', tmp_path / 'data' / 'config.json')
    monkeypatch.setattr(voice_registry, 'CLONED_DIR', tmp_path / 'data' / 'cloned')
    return voice_registry.VoiceRegistry()


def test_builtin_voice_can_be_looked_up(monkeypatch, tmp_path):
    registry = registry_in_tmp_path(monkeypatch, tmp_path)
    voice = registry.get_voice('alba')
    assert voice is not None
    assert voice['name'] == 'Alba'


def test_search_filters_voices(monkeypatch, tmp_path):
    registry = registry_in_tmp_path(monkeypatch, tmp_path)
    voices = registry.get_all_voices(search='cosette')
    assert [voice['id'] for voice in voices] == ['cosette']


def test_cloned_voice_can_be_added_and_removed(monkeypatch, tmp_path):
    registry = registry_in_tmp_path(monkeypatch, tmp_path)
    voice = registry.add_cloned_voice('cloned_test', 'Test Voice', 'test.safetensors', 'en')
    assert voice['is_cloned'] is True
    assert registry.get_voice('cloned_test')['name'] == 'Test Voice'
    assert registry.remove_cloned_voice('cloned_test') is True
    assert registry.get_voice('cloned_test') is None