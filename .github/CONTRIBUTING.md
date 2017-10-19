
# Contributing

Firstly, thanks for taking the time to contribute! :grin:

## What should I know before getting started?
- git
- python (reading and understanding code)

## How Can I Contribute?
### Feature suggestions / bug reports
You can contribute to this project by suggesting features or filing bugs by creating an issue [here](https://github.com/govbr/mpdg-govbr-faleconosco/issues/new).

### Setup
```bash
# Fork, then clone the repo
$ git clone git@github.com:<your-username>/mpdg-govbr-faleconosco.git

# create a virtualenv
$ virtualenv venv  

# activate the virtualenv
$ . venv/bin/activate

# Create the install env
$ python bootstrap.py 
$ bin/buildout

# test it
$ bin/code-analysis
$ bin/test
# to exit the virtualenv, just type 'deactivate' without quotes

```
#### Code conventions

Please follow http://identidade-digital-de-governo-plone.readthedocs.io/en/latest/contribuicoes/ (in portuguese)

#### Sending a pull request
Push to your fork and [submit a pull request](https://github.com/govbr/mpdg-govbr-faleconosco/compare/). Follow the [pull request template](https://github.com/govbr/mpdg-govbr-faleconosco/blob/master/.github/PULL_REQUEST_TEMPLATE.md)  

## Github labels
### Issue labels
- Labels starting with `module: `: these specify the modules in which the changes / enhancements are to be made.
- `bug`: it's a bug
- `enhancement`: hacking on the existing code
- Labels starting with `difficulty: `: specify the difficulty levels of the issue, depending on the work to be done to complete it.
- `new feature`: new feature introduced
