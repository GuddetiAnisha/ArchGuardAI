from archguard.parser import normalize, split_passages


def test_normalize_and_split():
    text = normalize("Title\r\n\r\n\r\nTLS   enabled\n")
    assert "\r" not in text
    assert "TLS enabled" in text
    passages = split_passages(text, max_chars=20)
    assert len(passages) >= 1
