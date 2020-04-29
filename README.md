# quantecon-mini-example
A short example showing how to write a lecture series using Jupyter Book 2.0.

## Creating an environment

1. `conda env create -f environment.yml`
2. `conda activate qe-mini-example`

## Building a Jupyter Book
Run the following command in your terminal: `jb build mini_book/`. If you would like to work with a clean build, you can empty the build folder by running `jb clean mini_book/`. If the jupyter execution is cached, this command will not delete the cached folder. To remove the build folder, you can run `jb clean --all mini_book/`.

## Publishing this Jupyter Book

Run `ghp-import -n -p -f mini_book/_build/html`.
If you are working on improving the quantecon-mini-example, the publishing of your work is taken care by Github workflows.
