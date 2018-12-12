# Email Automater

This program automates html emails from a Word Doc using Python.

### Requirements

To use this email automater you must have [Python](https://www.python.org/) Version 3.0 or newer.
To check if you have Python installed, go to your terminal and type:
```sh
$ python -V
```
The result should be: "Python 3.6.5" or whatever version you installed.
### Getting Ready
To run the program, go to your terminal into the project folder and do the following:
Create a virtual environment for the project:
```sh
$ cd app/
$ pip3 install virtualenv
$ virtualenv env
```

This will install a virtual environment in a folder within the app called env/.


Now you have to activate the viertual environment and install dependencies:

```sh
$ source env/bin/activate
```
At this point your terminal should have a (env) before your info in the terminal. Something like this (In Mac):

```sh
(env) user-mbp-2:app user$
```

### Running the Program
To run the program install all of the dependencies:
```sh
(env) $ pip install -r requirements.txt
```

After you install the dependencies you can run the program with:

```sh
(env) $ python3 run.py
```

### Deactivating the virtualenv
To deactivate the virtualenv type the following:

```sh
(env) $ deactivate
```
