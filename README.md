# Actuaries' Analytics Cookbook

*"Actuaries can be at a loss as to where to begin. But they often have the problem statement already.  What my teams have found useful are a few simple off the shelf solutions tailored to them that they can expand on. Given that, they usually pick it up an run with it. "*

A cookbook to help actuaries get started with a project using [Jupyter Book 2.0](https://jupyterbook.org/).

## Adding to the notebook

Generally to add content, one would:
 1.  Make sure the .ipynb file has been fully executed,
 2.  Add .ipynb files to the ``cookbook\docs`` subfolder,
 3.  Add those files to the ``cookbook\_toc.yml``

Full instructions [here](https://jupyterbook.org/start/create.html).

### Publishing this Jupyter Book

This repository is published automatically to `gh-pages` upon `push` to the `master` branch.

A `requirements.txt` file is provided to support this `CI` application.

## Local preview

If you wish to build and preview the site on the local machine, you will need to follow these instructions:

### Creating an Conda Environment

The conda environment is provided as `environment.yml`. This environment is used for all testing by Github Actions and can be setup by:

1. `conda env create -f environment.yml`
2. `conda activate qe-mini-example`

### Building a Jupyter Book

Run the following command in your terminal:

```bash
jb build cookbook/
```

If you would like to work with a clean build, you can empty the build folder by running:

```bash
jb clean cookbook/
```

If jupyter execution is cached, this command will not delete the cached folder.

To remove the build folder (including `cached` executables), you can run:

```bash
jb clean --all cookbook/
```
