from clean import normalize_name, normalize_email, normalize_phone, normalize_state, normalize_date


def test_name_cleans_messy():
    assert normalize_name(" ALLISON") == "Allison"
    assert normalize_name("maddox ") == "Maddox"
    assert normalize_name("mary ann") == "Mary Ann"


def test_name_missing():
    assert normalize_name(None) is None
    assert normalize_name("   ") is None


def test_email_cleans_messy():
    assert normalize_email(" DJ@Example.COM") == "dj@example.com"
    assert normalize_email("LISA.CLAYTON317@EXAMPLE.COM") == "lisa.clayton317@example.com"


def test_email_missing():
    assert normalize_email(None) is None
    assert normalize_email("") is None


def test_phone_cleans_messy():
    assert normalize_phone("(018) 451-4627") == "0184514627"
    assert normalize_phone("433.218.1960") == "4332181960"
    assert normalize_phone("868-240-5166") == "8682405166"
    assert normalize_phone("+1 7465642601") == "7465642601"


def test_phone_missing_or_too_short():
    assert normalize_phone(None) is None
    assert normalize_phone("") is None
    assert normalize_phone("12345") is None


def test_state_cleans_messy():
    assert normalize_state("ma") == "MA"
    assert normalize_state("Massachusetts") == "MA"
    assert normalize_state(" NEW JERSEY") == "NJ"
    assert normalize_state("NH") == "NH"


def test_state_missing_or_unknown():
    assert normalize_state(None) is None
    assert normalize_state("") is None
    assert normalize_state("Texas") is None


def test_date_cleans_messy():
    assert normalize_date("5/21/2009") == "2009-05-21"
    assert normalize_date("05/21/2009") == "2009-05-21"
    assert normalize_date("2008-07-22") == "2008-07-22"


def test_date_missing_or_invalid():
    assert normalize_date(None) is None
    assert normalize_date("") is None
    assert normalize_date("21/05/2009") is None
    assert normalize_date("hello") is None
