# Apex Documentation

## Make the docs locally

### Tool Installation

In order to build the documentation in this folder, you need ot have Sphinx-doc installed. Follow the [instructions here](https://www.sphinx-doc.org/en/master/usage/installation.html) for your specific OS.

For example, on Debian/Ubuntu:

    apt-get install python3-sphinx 

For OSX:

    brew install sphinx-doc

Anaconda

    conda install sphinx

Document building also requires make and dev tools.

### Build the docs

Once installed, you can use the make command to build the docs, for help simply type `make` in the `docs` director

    cd docs
    make

For an example, if you wanted to build the docs as HTML, you would use

    make html

After running this command you should see "Build finished. The HTML pages are in build/html." To view your docs you can simply open them with a browser:

   cd html

and then open `index.html` in your browser.







