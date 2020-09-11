from distutils.core import setup
setup(
    name = 'srcli',
    packages = ['srcli'],
    version = '1.1',
    description = "Sagi Rosenthal's CLI for interacting with jfrog artifactory using REST API",
    author = 'Sagi Rosenthal',
    author_email = 'mrsagi.rose@gmail.com',
    url = "",
    keywords = ['jfrog', 'artifactory', 'cli','api'],
    install_requires=[            # I get to this in a second
        'argparse',
        'urllib3',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3.7',
    ],
)