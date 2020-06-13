from setuptools import setup
from os.path import join, dirname

setup(
    name='lastfm-cli-scrobbler',
    version='0.0.1',
    description='Last.fm CLI Scrobbler',
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    long_description_content_type='text/markdown',
    url='http://github.com/maximtrp/lastfm-cli-scrobbler',
    author='Maksim Terpilowski',
    author_email='maximtrp@gmail.com',
    license='BSD',
    packages=['lastfm_cli_scrobbler'],
    keywords='python lastfm cli scrobbler',
    install_requires=['mutagen', 'requests', 'pylast'],
    entry_points={
        'console_scripts': [
            'scrobble=lastfm_cli_scrobbler.last_my:main',
            'scrobble2=lastfm_cli_scrobbler.last_pylast:main'
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Information Technology',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Home Automation',
        'Topic :: Internet',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
        'Programming Language :: Python :: 3.8'
    ],
    zip_safe=False)
