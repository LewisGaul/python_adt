import runpy

import setuptools


metadata = runpy.run_path("adt/metadata.py")

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="adt",
    version=metadata["__version__"],
    author="Lewis Gaul",
    maintainer="Lewis Gaul",
    contact_email="lewis.gaul@gmail.com",
    description="Algebraic Data Types in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha",
    ],
    packages=setuptools.find_packages(include=("adt",)),
    python_requires=">=3.6",
    install_requires=[],
    zip_safe=False,  # It may be safe, but force no zip for now.
)
