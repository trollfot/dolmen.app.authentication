from setuptools import setup, find_packages
from os.path import join

name = 'dolmen.app.authentication'
version = '0.1'
readme = open("README.txt").read()
history = open(join('docs', 'HISTORY.txt')).read().replace(name + ' - ', '')

test_requires = [
]

setup(name = name,
      version = version,
      description = 'Dolmen CMS authentication package',
      long_description = readme[readme.find('\n\n'):] + '\n' + history,
      keywords = 'Grok Zope3 CMS Dolmen',
      author = 'Souheil Chelfouh',
      author_email = 'souheil@chelfouh.com',
      url = 'http://tracker.trollfot.org/',
      download_url = 'http://pypi.python.org/pypi/dolmen.app.authentication',
      license = 'GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages = ['dolmen', 'dolmen.app'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      extras_require={'test': test_requires},
      install_requires=[
          'dolmen.app.layout',
          'dolmen.app.security',
          'dolmen.app.site',
          'dolmen.authentication',
          'dolmen.content',
          'dolmen.forms.base',
          'grok',
          'grokcore.view',
          'megrok.menu',
          'setuptools',
          'wc.cookiecredentials>=3.9',
          'z3c.schema',
          'zope.authentication',
          'zope.component',
          'zope.container',
          'zope.event',
          'zope.formlib',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.pluggableauth',
          'zope.principalregistry',
          'zope.publisher',
          'zope.schema',
          'zope.security',
          'zope.securitypolicy',
          'zope.site',
          'zope.traversing',
      ],
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Grok',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
      ],
)
