import re
from setuptools import setup, find_packages

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

version = ''
with open('openrobot_cli/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')

readme = ''
with open('README.md') as f:
    readme = f.read()

setup(
    name='openrobot-cli',
    version=version,
    description='OpenRobot CLI',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='OpenRobot',
    py_modules=['openrobot-cli'],
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'openrobot-cli=openrobot_cli:cli',
            'openrobot=openrobot_cli:cli',
        ],
    },
)