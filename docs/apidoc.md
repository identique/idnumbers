# Generate the API doc for this project

We survey the doc gen tools at the [issue #80](https://github.com/microdataxyz/idnumbers/issues/80). In the end, we
would like to use the simplest tool, [pdoc](https://pdoc.dev/). It generates the api docs based on
[docstring](https://peps.python.org/pep-0257/).

We could run the following script to install:

```shell
python -m virtualenv doc_env
doc_env/bin/activate

pip install pdoc
```

And run it:
```shell
pdoc -o pdocs --footer-text "idnumbers $(cat ./VERSION)+, dev version included" idnumbers !idnumbers.nationalid.test_*
```

It outputs the API docs to a folder named `pdocs`. Have fun with it!
