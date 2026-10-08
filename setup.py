from setuptools import setup

setup(
    name="indexclient",
    # A fork source install must not depend on GitHub copying upstream tags.
    version="2.3.1+mmrf.visibility",
    packages=["indexclient", "indexclient.parsers"],
    install_requires=["requests>=2.5.2,<3.0.0"],
)
