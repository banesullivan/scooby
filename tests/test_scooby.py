import datetime
from importlib.metadata import distribution
import json
import os
import re
import subprocess
import sys
from types import SimpleNamespace

from bs4 import BeautifulSoup
import numpy
import pytest

import scooby

# Write a package `dummy_module` without version number.
ppath = os.path.join("tests", "dummy_module")
try:
    os.mkdir(ppath)
except FileExistsError:
    pass

with open(os.path.join(ppath, "__init__.py"), "w") as f:
    f.write("info = 'Package without __version__ number.'\n")

sys.path.append('tests')


def test_report():
    report = scooby.Report()
    text = str(report)
    assert len(text) > 0
    assert len(report.packages) > 0
    for pkg, vers in report.packages.items():
        assert isinstance(pkg, str)
        assert isinstance(vers, str)
    report = scooby.Report(core='numpy')
    assert 'numpy' in report.packages
    html = report._repr_html_()
    assert len(html) > 0
    # Same as what is printed in Travis build log
    report = scooby.Report(additional=['pytest', 'foo'])
    report = scooby.Report(
        additional=[
            'foo',
        ]
    )
    report = scooby.Report(
        additional=[
            pytest,
        ]
    )
    report = scooby.Report(additional=pytest)
    report = scooby.Report(additional=['collections', 'foo', 'aaa'], sort=True)


def test_timezone(monkeypatch):
    # Patch datetime to simulate non-UTC system time
    class FixedDatetime(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            # Return a fixed time in, e.g., US/Eastern (UTC-5)
            return datetime.datetime(
                2025, 1, 1, 12, 0, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=-5))
            )

    monkeypatch.setattr(datetime, "datetime", FixedDatetime)
    assert 'UTC' in str(scooby.Report())


# Global fake packages dict
FAKE_INSTALLED_PACKAGES = {
    "numpy": "1.27.0",
    "scipy": "1.12.0",
    "misc_pkg1": "0.1",
    "misc_pkg2": "0.2",
}


def fake_distributions():
    """Yield fake Distribution-like objects from the global dict."""
    for name, version in FAKE_INSTALLED_PACKAGES.items():
        yield SimpleNamespace(metadata={"Name": name, "Version": version})


def test_dict(monkeypatch):
    # Patch distributions to return fake installed packages
    monkeypatch.setattr("importlib.metadata.distributions", fake_distributions)
    report = scooby.Report(['no_version', 'does_not_exist'], show_other=True)
    report_repr = repr(report)

    # Test regular dict items separately from other items
    report_dict = report.to_dict()
    assert 'other' in report_dict.keys()
    other = report_dict.pop('other')

    for key, value in report_dict.items():
        if key != 'MKL':
            assert key in report_repr
        assert value[:10] in report_repr

    # Test other items (converted from JSON)
    other_dict = json.loads(other)
    for key, value in other_dict.items():
        assert key in report_repr


def test_inheritence_example():
    class Report(scooby.Report):
        def __init__(self, additional=None, ncol=3, text_width=80, sort=False):
            """Initiate a scooby.Report instance."""

            # Mandatory packages.
            core = ['psutil', 'mkl', 'numpy', 'scooby']

            # Optional packages.
            optional = [
                'your_optional_packages',
                'e.g.',
                'matplotlib',
                'foo',
            ]

            scooby.Report.__init__(
                self,
                additional=additional,
                core=core,
                optional=optional,
                ncol=ncol,
                text_width=text_width,
                sort=sort,
            )

    report = Report(['pytest'])
    assert 'psutil' in report.packages
    assert 'mkl' in report.packages
    assert 'numpy' in report.packages


def test_ipy():
    scooby.in_ipykernel()


def test_get_version():
    name, version = scooby.get_version(numpy)
    assert version == numpy.__version__
    assert name == "numpy"

    # Package that was no version given by owner; gets 0.1.0 from setup/pip
    name, version = scooby.get_version("no_version")
    assert version == "0.1.0"
    assert name == "no_version"

    # Dummy module without version (not installed properly)
    name, version = scooby.get_version("dummy_module")
    assert version == scooby.report.VERSION_NOT_FOUND
    assert name == "dummy_module"

    name, version = scooby.get_version("does_not_exist")
    assert version == scooby.report.MODULE_NOT_FOUND
    assert name == "does_not_exist"


def test_plain_vs_html():
    report = scooby.Report()
    text_html = BeautifulSoup(report._repr_html_(), features="html.parser").get_text()
    text_plain = report.__repr__()

    text_plain = " ".join(re.findall("[a-zA-Z1-9]+", text_plain))
    text_html = " ".join(re.findall("[a-zA-Z1-9]+", text_html))

    # Plain text currently starts with `Date :`;
    # we should remove that, or add it to the html version too.
    assert text_html[20:] == text_plain[25:]


def test_extra_meta():
    report = scooby.Report(extra_meta=("key", "value"))
    assert "key : value" in report.__repr__()
    report = scooby.Report(extra_meta=(("key", "value"),))
    assert "key : value" in report.__repr__()
    report = scooby.Report(extra_meta=(("key", "value"), ("another", "one")))
    assert "key : value" in report.__repr__()
    assert "another : one" in report.__repr__()
    with pytest.raises(TypeError):
        report = scooby.Report(extra_meta=(("key", "value"), "foo"))
    with pytest.raises(TypeError):
        report = scooby.Report(extra_meta="foo")
    with pytest.raises(TypeError):
        report = scooby.Report(extra_meta="for")


@pytest.mark.skipif(sys.version_info.major < 3, reason="Tracking not supported on Python 2.")
def test_tracking():
    scooby.track_imports()
    from scipy.constants import mu_0  # noqa ; a float value

    report = scooby.TrackedReport()
    scooby.untrack_imports()
    import dummy_module  # noqa
    import no_version  # noqa

    assert "numpy" in report.packages
    assert "scipy" in report.packages
    assert "no_version" not in report.packages
    assert "dummy_module" not in report.packages
    assert "pytest" not in report.packages
    assert "mu_0" not in report.packages


def test_version_compare():
    assert scooby.meets_version('2', '1')
    assert not scooby.meets_version('1', '2')

    assert scooby.meets_version('1', '1')
    assert scooby.meets_version('0.1', '0.1')
    assert scooby.meets_version('0.1.0', '0.1.0')

    assert scooby.meets_version('1.0', '0.9')
    assert not scooby.meets_version('0.9', '1.0')

    assert scooby.meets_version('0.2.5', '0.1.8')
    assert not scooby.meets_version('0.1.8', '0.2.5')

    assert not scooby.meets_version('0.25.1', '0.25.2')
    assert scooby.meets_version('0.26.0', '0.25.2')
    assert scooby.meets_version('0.25.2', '0.25.2')

    assert not scooby.meets_version('0.25.2', '0.26')

    assert scooby.meets_version('0.28.0dev0', '0.25.2')

    with pytest.raises(ValueError):
        scooby.meets_version('0.25.2.0', '0.26')


def test_import_os_error():
    # pyvips requires libvips, etc., to be installed
    # We don't have this on CI, so this should throw an error on import
    # Make sure scooby can handle it.
    with pytest.raises(OSError):
        import pyvips  # noqa
    assert scooby.Report(['pyvips'])


@pytest.mark.skipif(not sys.platform.startswith('linux'), reason="Not Linux.")
def test_import_time():
    # Relevant for packages which provide a CLI:
    # How long does it take to import?
    cmd = ["time", "-f", "%U", sys.executable, "-c", "import scooby"]
    # Run it twice, just in case.
    subprocess.run(cmd)
    subprocess.run(cmd)
    # Capture it
    out = subprocess.run(cmd, capture_output=True)

    # Currently we check t < 0.2 s.
    assert float(out.stderr.decode("utf-8")[:-1]) < 0.2


@pytest.mark.script_launch_mode('subprocess')
def test_cli(script_runner):
    # help
    for inp in ['--help', '-h']:
        ret = script_runner.run(['scooby', inp])
        assert ret.success
        assert "Great Dane turned Python environment detective" in ret.stdout

    def rep_comp(inp):
        # Exclude time to avoid errors.
        # Exclude scooby-version, because if run locally without having scooby
        # installed it will be "unknown" for the __main__ one.
        out = inp.split('OS :')[1]
        if 'scooby' in inp:
            out = out.split('scooby :')[0]
        else:  # As the endings are different.
            out = out.split('--------')[0]
        return out

    # default: scooby-Report
    ret = script_runner.run(['scooby'])
    assert ret.success
    assert rep_comp(scooby.Report().__repr__()) == rep_comp(ret.stdout)

    # default: scooby-Report with sort and no-opt
    ret = script_runner.run(['scooby', 'numpy', '--no-opt', '--sort'])
    assert ret.success
    test = scooby.Report('numpy', optional=[], sort=True).__repr__()
    print(rep_comp(test))
    print(rep_comp(ret.stdout))
    assert rep_comp(test) == rep_comp(ret.stdout)

    # version -- VIA scooby/__main__.py by calling the folder scooby.
    ret = script_runner.run([sys.executable, 'scooby', '--version'])
    assert ret.success
    assert "scooby v" in ret.stdout

    # version -- VIA scooby/__main__.py by calling the file.
    ret = script_runner.run([sys.executable, os.path.join('scooby', '__main__.py'), '--version'])
    assert ret.success
    assert "scooby v" in ret.stdout

    # default: scooby-Report for matplotlibe
    ret = script_runner.run(['scooby', '--report', 'pytest'])
    assert ret.success
    assert "pytest" in ret.stdout
    assert "iniconfig" in ret.stdout

    # handle error -- no distribution
    ret = script_runner.run(['scooby', '--report', 'pathlib'])
    assert not ret.success
    assert "importlib" in ret.stderr

    # handle error -- not found
    ret = script_runner.run(['scooby', '--report', 'foobar'])
    assert not ret.success
    assert "no Report" in ret.stderr


def test_auto_report():
    report = scooby.AutoReport('pytest')
    assert 'pytest' in report.packages
    assert 'iniconfig' in report.packages


@pytest.mark.parametrize(
    "requirement, expected",
    [
        ("x==0.4", "x"),
        ("x<0.2", "x"),
        ("x!=0.42", "x"),
        ("y>1.0", "y"),
        ("z; python_version<'3.10'", "z"),
        ("w >= 1.2", "w"),
        ("x @ git+https://github.com/foo/bar.git@main", "x"),
    ],
)
def test_get_distribution_dependencies(monkeypatch, requirement, expected):
    class FakeDist:
        requires = [requirement]

    def fake_distribution(dist_name):
        return FakeDist()

    monkeypatch.setattr("scooby.report.distribution", fake_distribution)

    deps = scooby.report.get_distribution_dependencies("fakepkg")
    assert deps == [expected]


def test_get_distribution_dependencies_no_deps():
    deps = scooby.report.get_distribution_dependencies('numpy')
    assert deps == []
    deps = scooby.report.get_distribution_dependencies('numpy', separate_extras=True)
    assert deps == {'core': [], 'optional': {}}


def test_get_distribution_dependencies_uniqueness_and_order(monkeypatch):
    class FakeDist:
        requires = ["y==0.42", "x<1.5", "x>1.0"]

    def fake_distribution(dist_name):
        return FakeDist()

    monkeypatch.setattr("scooby.report.distribution", fake_distribution)

    deps = scooby.report.get_distribution_dependencies("fakepkg")

    # 'y' comes first, then 'x' (deduplicated but ordered by first occurrence)
    assert deps == ["y", "x"]


def test_get_distribution_dependencies_separate_extras():
    all_deps = scooby.report.get_distribution_dependencies("beautifulsoup4", separate_extras=False)
    assert all_deps == [
        "soupsieve",
        "typing-extensions",
        "cchardet",
        "chardet",
        "charset-normalizer",
        "html5lib",
        "lxml",
    ]

    separate_deps = scooby.report.get_distribution_dependencies(
        "beautifulsoup4", separate_extras=True
    )
    assert separate_deps == {
        'core': ['soupsieve', 'typing-extensions'],
        'optional': {
            'cchardet': ['cchardet'],
            'chardet': ['chardet'],
            'charset-normalizer': ['charset-normalizer'],
            'html5lib': ['html5lib'],
            'lxml': ['lxml'],
        },
    }

    # Flatten back into one list
    flat_list = separate_deps["core"] + [
        pkg for dep_list in separate_deps["optional"].values() for pkg in dep_list
    ]
    assert flat_list == all_deps

    # Check that optional keys match actual extras from distribution
    dist = distribution("beautifulsoup4")
    extras_names = list(dist.metadata.get_all("Provides-Extra") or [])
    assert list(separate_deps["optional"].keys()) == extras_names
