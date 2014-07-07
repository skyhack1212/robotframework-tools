from six import PY2


PROJECT = 'robotframework-tools'

exec(open('zetup.py'))


REQUIRES += (
  'robotframework >= 2.8' if PY2
  else 'robotframework-python3 >= 2.8.4'
  )


setup(
  name=PROJECT,
  version=VERSION,
  description=(
    'Python Tools for Robot Framework and Test Libraries.'
    ),
  author='Stefan Zimmermann',
  author_email='zimmermann.code@gmail.com',
  url='http://bitbucket.org/userzimmermann/robotframework-tools',

  license='GPLv3',

  install_requires=REQUIRES,
  extras_require=EXTRAS,

  packages=[
    'robottools',
    'robottools.library',
    'robottools.library.keywords',
    'robottools.library.session',
    'robottools.library.context',
    'robottools.library.inspector',
    'robottools.testrobot',
    'robottools.remote',
    'robotshell',
    'robotshell.magic',
    ],
  py_modules=[
    'ToolsLibrary',
    ],

  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Topic :: Software Development',
    'Topic :: Utilities',
    ],
  keywords=[
    'robottools', 'robot', 'framework', 'robotframework', 'tools',
    'test', 'automation', 'testautomation',
    'testlibrary', 'testcase', 'keyword', 'pybot',
    'robotshell', 'ipython',
    'python3',
    ],
  )
