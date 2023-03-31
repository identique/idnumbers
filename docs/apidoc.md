# Generate the API doc for this project

We survey the doc gen tools at the [issue #80](https://github.com/Identique/idnumbers/issues/80). In the end, we
would like to use the simplest tool, [pydoctor](https://pydoctor.readthedocs.io/en/latest/index.html). It generates the api docs based on
[docstring](https://peps.python.org/pep-0257/).

We could run the following script to install:

```shell
python -m virtualenv doc_env
doc_env/bin/activate

pip install pydoctor
```

And run it:
```shell
pydoctor --make-html --html-output=docs/$(cat ./VERSION) --project-name="idnumbers" --project-version=$(cat ./VERSION) --project-url=https://github.com/identique/idnumbers --template-dir=./docs/template idnumbers
```

It outputs the API docs to a folder named `docs/version`. Have fun with it!
