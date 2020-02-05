from distutils.core import setup

setup(name='ub-split-map' ,
    version='0.2.0' ,
    author='Jay Deiman' ,
    author_email='admin@splitstreams.com' ,
    url='http://stuffivelearned.org' ,
    description='A python module for Unbound to dynamically map external ' \
        'IPs to internal RFC 1918 addresses to avoid split-horizon DNS' ,
    long_description='Full documentation is available at ' \
        'https://stuffivelearned.org/doku.php?id=os:linux:general:splitdns' ,
    py_modules=['ubsplitmap'] ,
    data_files=[ ('etc/unbound' , ['ub-split-map.ini.default']) ] ,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha' ,
        'Intended Audience :: Developers' ,
        'Intended Audience :: Information Technology' ,
        'Intended Audience :: System Administrators' ,
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)' ,
        'Natural Language :: English' ,
        'Operating System :: OS Independent' ,
        'Programming Language :: Python :: 3' ,
        'Topic :: Internet :: Name Service (DNS)' ,
    ]
)
