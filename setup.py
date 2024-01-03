from setuptools import setup, find_packages

VERSION = "1.0.2"
# Runtime dependencies. See requirements.txt for development dependencies.
DEPENDENCIES = [
    "aiohttp==3.9.1",
]

setup(
    name="ewelink",
    version=VERSION,
    description="Ewelink API",
    url="https://github.com/dantimofte/ewelink-api-python",
    license="",
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    include_package_data=True,
    keywords=[],
    classifiers=[],
    zip_safe=True,
    entry_points={},
)
