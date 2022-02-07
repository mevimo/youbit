from setuptools import setup

setup(
    name='YouBit',
    version='0.1.0',    
    description='Encoding files into video\'s that survives  ', ##TODO
    url='https://github.com/mevimo/youbit',
    author='Florian Laporte',
    author_email='florianlaporte@pm.me',
    license='MIT License',
    packages=['youbit'],
    install_requires=['mpi4py>=2.0', ##TODO
                      'numpy',                     
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',  
        'Operating System :: OS Independent',      
        'Programming Language :: Python :: 3.10',
    ],
)
