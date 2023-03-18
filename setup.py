"""Setup script for maildaemon package."""

import setup_boilerplate


class Package(setup_boilerplate.Package):
    """Package metadata."""

    name = 'maildaemon'
    description = 'Multi-server mail filtering daemon supporting IMAP, POP and SMTP.'
    url = 'https://github.com/mbdevpl/maildaemon'
    classifiers = [
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities'
        ]
    keywords = ['e-mail', 'filter', 'daemon', 'imap', 'pop', 'smtp']
    entry_points = {
        'console_scripts': [
            'maildaemon = maildaemon.__main__:main'
            ]
        }


if __name__ == '__main__':
    Package.setup()
