# quantecon-mini-example
A short example showing how to write a lecture series using Jupyter Book 2.0.

### Creating an environment

Given that [cli](https://github.com/ExecutableBookProject/cli), [MyST-NB](https://github.com/ExecutableBookProject/MyST-NB), [sphinx-book-theme](https://github.com/ExecutableBookProject/sphinx-book-theme) are still work-in-progress, make sure to fetch the latest master branch from each repository and update your conda environment by following these steps:

1. Clone the following repositories: [cli](https://github.com/ExecutableBookProject/cli), [MyST-NB](https://github.com/ExecutableBookProject/MyST-NB), [sphinx-book-theme](https://github.com/ExecutableBookProject/sphinx-book-theme)
2. `conda create -n venv_name pip QuantEcon matplotlib`
3. Activate conda environment
4. Find the venv folder under the anaconda directory. It could look something like this: `/anaconda3/envs/venv_name/`
5. For each of the cloned repositories run the following: `/anaconda3/envs/venv_name/bin/pip install -e.`

### Building a Jupyter Book

Run the following command in your terminal: `jb build mini_book/`.

### Publishing this Jupyter Book

Run `ghp-import -n -p -f mini_book/_build/html`
