# coding=utf-8
import io

import setuptools

__version__ = '0.6.0'

with io.open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="scooby",
    version=__version__,
    author="Dieter Werthmüller & Bane Sullivan",
    author_email="info@pyvista.org",
    description="A Great Dane turned Python environment detective",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/banesullivan/scooby",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
    ),
    python_requires='>=3.7.*',
    extras_require={
        'cpu': ['psutil', 'mkl'],
        # 'gpu': [], # TODO: what's needed?
    },
)
