# Actuaries' Analytical Cookbook

*"Actuaries can be at a loss as to where to begin. But they often have the problem statement already.  What my teams have found useful are a few simple off the shelf solutions tailored to them that they can expand on. Given that, they usually pick it up an run with it. "*

A cookbook to help actuaries get started with data and analytics projects in both data science and traditional fields, using [Jupyter Book 2.0](https://jupyterbook.org/).

## Workflow

### Adding notebooks to the cookbook

Generally to add content to the book, one could:

 1.  Create a fork
 2.  Make sure the .ipynb file has been fully executed [1],
 3.  Add .ipynb files to the ``cookbook\docs`` subfolder,
 4.  Add those files to the ``cookbook\_toc.yml``
 5.  Go to Actions and enable "Build HTML and Deploy to GH-PAGES" (on the right hand side)
 6.  Go a random file (e.g. _toc_yml), add an empty space and commit to ``main`` in the fork
 7.  Go back to Actio and see if a workflow has been enabled. Wait for it to finish and check that the website at https://[yourusername].github.io/cookbook works as intended
 8.  Create a pull request to ``main`` in the [https://github.com/ActuariesInstitute/cookbook](https://github.com/ActuariesInstitute/cookbook) repository.
 9.  Future workflows will be enabled automatically.

Reference Jupyter book documentation [here](https://jupyterbook.org/start/create.html).

### Publishing this Jupyter Book

This repository is published automatically to `gh-pages` upon `push` to the `main` branch.

[1] Jupyter book runs notebooks automatically if there are missing outputs. A `requirements.txt` file is provided to support this `CI` application.

## Local preview

This should not be needed but if you wish to build and preview the site on the local machine, you will need to follow these instructions:

### Creating an Conda Environment

The conda environment is provided as `environment.yml`. This environment is used for all testing by Github Actions and can be setup by:

1. `conda env create -f environment.yml`
2. `conda activate main-conda-env`

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
