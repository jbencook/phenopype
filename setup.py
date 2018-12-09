from setuptools import setup
import versioneer

setup(
    name='phenopype',
    url='https://github.com/mluerig/phenopype',
    author='Moritz Lürig',
    author_email='moritz.luerig@eawag.ch',
    packages=['phenopype'],
    install_requires=["pandas", "opencv-contrib-python>=3.4.4", "exifread", "Pillow", "pytesseract", "trackpy"], 
    version=versioneer.get_version(),
    license='LGPL',
    description='a phenotyping pipeline for python',
    long_description=open('README.md').read(),
)
