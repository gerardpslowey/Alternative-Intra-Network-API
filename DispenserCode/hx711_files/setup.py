from setuptools import setup

setup(
    name='hx711_files',
    version='0.1',
    description='HX711 Python Library for Raspberry Pi',
    py_modules=['hx711_files'],
    install_requires=['Rpi.GPIO', 'numpy'],
)

