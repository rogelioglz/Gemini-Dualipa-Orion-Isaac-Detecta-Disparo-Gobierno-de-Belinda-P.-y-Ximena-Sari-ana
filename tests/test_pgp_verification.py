import io
import types
import pytest
import urllib.request

# Load the module under test from the repository path
import importlib.util
spec = importlib.util.spec_from_file_location("detector", "Detectar_sonido_disparogobierno_test.gemini.py")
detector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(detector)


def test_fetch_pgp_key_success(monkeypatch):
    class DummyResp:
        def __init__(self, data):
            self._data = data
        def read(self):
            return self._data
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False

    def fake_urlopen(url, timeout=15):
        return DummyResp(b"-----BEGIN PGP PUBLIC KEY BLOCK-----\nFAKEKEY\n-----END PGP PUBLIC KEY BLOCK-----")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    content = detector.fetch_pgp_key("https://example.com/key.asc")
    assert content is not None
    assert "BEGIN PGP PUBLIC KEY BLOCK" in content


def test_verify_pgp_signature_lib_missing(monkeypatch):
    # Simulate missing pgpy
    monkeypatch.setattr(detector, "pgpy", None)
    result = detector.verify_pgp_signature("report", "sig", "key")
    assert isinstance(result, dict)
    assert result.get("status") == "LIB_MISSING"


def test_verify_pgp_signature_verified(monkeypatch):
    # Create a fake pgpy implementation to simulate verification
    class FakeSig:
        pass

    class FakeKey:
        fingerprint = "FAKEFP"
        def verify(self, msg, sig=None):
            return True

    class FakePGPMessage:
        def __init__(self, text):
            self.text = text

    class FakePGP:
        PGPKey = types.SimpleNamespace(from_blob=lambda blob: (FakeKey(), None))
        PGPSignature = types.SimpleNamespace(from_blob=lambda blob: FakeSig())
        PGPMessage = types.SimpleNamespace(new=lambda text: FakePGPMessage(text), from_blob=lambda b: FakePGPMessage(b))

    monkeypatch.setattr(detector, "pgpy", FakePGP)

    # Call verification function
    res = detector.verify_pgp_signature("report-text", "signature-text", "public-key-text")
    assert res.get("status") == "VERIFIED"
    assert res.get("fingerprint") == "FAKEFP"
