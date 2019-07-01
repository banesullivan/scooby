import re
import bs4
import scooby


def test_plain_html_are_the_same():
    # Get a `Report`-instance, containing packages with don't exist, and such
    # without a version number; also, containing all three lists.
    out = scooby.Report(
            [re, 'no_version'], ['does_not_exist', bs4], [scooby, 'numpy'])

    # Get html and plain text version of the repr.
    text_html = bs4.BeautifulSoup(out._repr_html_()).get_text()
    text_plain = out.__repr__()

    # Extract only letters and numbers.
    text_plain = " ".join(re.findall("[a-zA-Z1-9]+", text_plain))
    text_html = " ".join(re.findall("[a-zA-Z1-9]+", text_html))

    # Ensure they are the same.
    assert text_html == text_plain


def test_no_version():
    # Get a `Report`-instance.
    out = scooby.Report(['no_version'])

    assert scooby.report.VERSION_NOT_FOUND in out.__repr__()


def test_does_not_exist():
    # Get a `Report`-instance.
    out = scooby.Report(['does_not_exist'])

    assert scooby.report.MODULE_NOT_FOUND in out.__repr__()
