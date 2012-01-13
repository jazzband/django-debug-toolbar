from setuptools import setup, find_packages

setup(
    name='django-debug-toolbar',
    version='0.9.2',
    description='A configurable set of panels that display various debug information about the current request/response.',
    long_description=open('README.rst').read(),
    # Get more strings from http://www.python.org/pypi?:action=list_classifiers
    author='Rob Hudson',
    author_email='rob@cogit8.org',
    url='https://github.com/django-debug-toolbar/django-debug-toolbar',
    download_url='https://github.com/django-debug-toolbar/django-debug-toolbar/downloads',
    license='BSD',
    packages=find_packages(exclude=('ez_setup', 'tests', 'example')),
    tests_require=[
        'django>=1.1,<1.4',
        'dingus',
    ],
    test_suite='runtests.runtests',
    include_package_data=True,
    zip_safe=False,  # because we're including media that Django needs
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
