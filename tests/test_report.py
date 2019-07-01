import re
import scooby
from bs4 import BeautifulSoup


def test_plain_html_are_the_same():
    # Get a `Report`-instance.
    out = scooby.Report()

    # Get html and plain text version of the repr.
    text_html = BeautifulSoup(out._repr_html_()).get_text()
    text_plain = out.__repr__()

    # Extract only letters and numbers.
    text_plain = " ".join(re.findall("[a-zA-Z1-9]+", text_plain))
    text_html = " ".join(re.findall("[a-zA-Z1-9]+", text_html))

    # Ensure they are the same.
    assert text_html == text_plain
