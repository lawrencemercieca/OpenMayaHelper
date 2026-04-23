from setuptools import find_packages, setup


with open("README.md", "r", encoding="utf-8") as f:
    description = f.read()


setup(
    name="openmayahelper",
    version="0.1.0",
    description="OpenMaya-first helper package for PyMEL-style Maya workflows.",
    long_description=description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=False,
    install_requires=[],
    python_requires=">=3.10",
)
