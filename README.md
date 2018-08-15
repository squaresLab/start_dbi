# start_dbi

Provides the DBI module for START

## Installation

To avoid polluting the system's Python packages, we strongly recommend using
[pipenv](https://docs.pipenv.org/) or [virtualenv](https://packaging.python.org/guides/installing-using-pip-and-virtualenv/)
to perform an isolated installation. We recommend creating a dedicated virtual
environment for START using either of those tools. To establish such an
environment using `pipenv`, create a directory on your machine for the purpose
and then call `pipenv --python 2.7` from inside that directory (n.b. a separate
virtual environment may be created for Python 3 by calling `pipenv --python 3.5`
in a different directory. Once the virtual environment has been created, you can
"enter" the virtual environment by calling `pipenv shell` from inside the
directory. To "exit" the virtual environment, simply execute `exit`.

Before installing this particular module, you will need to first install
`start_core`. Clone the repository for `start_core` to your machine and execute
`pip install . --upgrade` at the root of the repository. You may wish to do the
same for `start_image` if you would like to use Docker to interact with the
system under test.

With all of its dependencies installed, this module can be installed by calling
`pip install . --upgrade` from the root of this repository.
