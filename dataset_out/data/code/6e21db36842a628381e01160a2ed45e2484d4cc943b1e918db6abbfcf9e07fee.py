from src.agents.ctdatenight_agents import FINAL_SETTINGS
from src.agents.output_normalizer import normalize_links, output_normalizer


def test_normalize_string_html():
    s = (
        '<p>See <a href="https://ctdatenight.com/deal">deal</a> or '
        'visit https://ctdatenight.com/page for more.</p>'
    )
    out = normalize_links(s)
    assert FINAL_SETTINGS["redirect_url"] in out
    assert "ctdatenight.com/deal" not in out
    assert "https://ctdatenight.com/page" not in out


def test_normalize_nested_dict():
    data = {"body": ["Check this https://ctdatenight.com/a", {"link": '<a href="/join">join</a>'}]}
    out = normalize_links(data)
    out_str = str(out)
    assert FINAL_SETTINGS["redirect_url"] in out_str
    assert "ctdatenight.com" not in out_str


def test_decorator_applies():
    @output_normalizer
    def sample():
        return {"text": "Visit https://ctdatenight.com/x"}

    res = sample()
    assert FINAL_SETTINGS["redirect_url"] in str(res)
    assert "ctdatenight.com" not in str(res)
