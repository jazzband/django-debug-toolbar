from setuptools import setup, find_packages

setup(
    name='django-debug-toolbar',
    version='0.9.4',
    description='A configurable set of panels that display various debug information about the current request/response.',
    long_description=open('README.rst').read(),
    author='Rob Hudson',
    author_email='rob@cogit8.org',
    url='https://github.com/django-debug-toolbar/django-debug-toolbar',
    download_url='https://github.com/django-debug-toolbar/django-debug-toolbar/downloads',
    license='BSD',
    packages=find_packages(exclude=('tests', 'example')),
    install_requires=[
        'django>=1.4.2,<1.6',
        'sqlparse',
    ],
    test_suite='runtests.runtests',
    include_package_data=True,
    zip_safe=False,                 # because we're including static files
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
