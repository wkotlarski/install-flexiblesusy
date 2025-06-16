# Script to install FlexibleSUSY

## Introduction
[FlexibleSUSY](https://github.com/FlexibleSUSY/FlexibleSUSY) relias on some and optionally can link to certain external libraries.
While this allows to use the state-of-the-art computations provided by these libraries and avoid mistakes caused by providing our own functions for doing, for example, basic matrix manipulations it also means that its instalation is not so straightword.

This script helps installing FlexibleSUSY on Linux.
  
## Usage
Example use
```
python3 install.py SM,MSSM
```
The last argument is a `,`-separated list of models you'd like to configure FlexibleSUSY with.

## Getting help
If the script doesn't work for you, please create an [Issue](https://github.com/wkotlarski/install-flexiblesusy/issues)
