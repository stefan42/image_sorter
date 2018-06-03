import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('LICENSE') as f:
    license = f.read()

setuptools.setup(
    name="image_sorter",
    version="0.4",
    author="Stefan Schmidt",
    author_email="stefanschmidt@web.de",
    description="A small script which collects images from different imput folders and sorts them by the date.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=license,
    url="https://github.com/stefan42/image_sorter",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'exifread',
    ],
    entry_points={
        'console_scripts': ['image_sorter=image_sorter.image_sorter:main'],
    }

)
