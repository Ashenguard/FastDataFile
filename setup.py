import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="FastDataFile",
    version="1.0.2",
    license='MIT License',
    author="Ashenguard",
    author_email="Ashenguard@agmdev.com",
    description="The ease of file datafiles",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ashenguard/fastdatafile",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    include_package_data=True,
    install_requires=["pyyaml"],
    dependency_links=[]
)
