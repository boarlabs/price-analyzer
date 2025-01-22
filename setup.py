
from setuptools import setup, find_packages


with open("requirements.txt", mode="r") as file_handler:
    REQUIREMENTS = file_handler.readlines()


setup(
    name="price_analyzer",
    version="0.1.0",
    description="Energy price analyzing utils",
    long_description="",
    long_description_content_type="text/markdown",
    url="https://github.com/boarlabs/price-analyzer",
    license="Proprietary",
    classifiers=[
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3.9"
    ],
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=REQUIREMENTS
)