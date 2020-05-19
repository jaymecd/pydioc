from setuptools import setup, find_packages
from pydioc import __version__

with open("README.md") as fd:
    readme = fd.read()

test_requirements = [
    "pytest>=5.4,<6.0",
]

setup(
    name="pydioc",
    description="Python DI/IoC container",
    python_requires=">3.7",
    version=__version__,
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Nikolai Zujev",
    author_email="nikolai.zujev@gmail.com",
    url="https://github.com/jaymecd/pydioc",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=False,
    keywords="dependency injection ioc container",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    project_urls={
        "Repository": "https://github.com/jaymecd/pydioc",
        "Bug Reports": "https://github.com/jaymecd/pydioc/issues",
        "Documentation": "https://github.com/jaymecd/pydioc",
    },
    test_suite="tests",
    tests_require=test_requirements,
    extras_require={"test": test_requirements},
)
