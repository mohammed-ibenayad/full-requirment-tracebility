from setuptools import setup

setup(
    name="pytest-json-reporter",
    version="0.1.0",
    description="Pytest plugin for test result reporting to JSON",
    author="Your Name",
    author_email="your.email@example.com",
    py_modules=["pytest_results_plugin"],
    install_requires=["pytest>=6.0.0"],
    entry_points={
        "pytest11": ["json_reporter = pytest_results_plugin"]
    },
    classifiers=[
        "Framework :: Pytest",
    ],
)