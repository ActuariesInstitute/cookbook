---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.3
kernelspec:
  display_name: R
  language: R
  name: ir
---

# Setting Up R

+++
By YAP and YDAWG members.

This document will help you to get ready with R. Original version as a Word document can be found [here](https://github.com/ActuariesInstitute/YAP-YDAWG-R-Workshop/raw/master/R_Session_Prework.docx).

+++

## Step 1 – Install base R
### Windows
 * Download the Windows R installer from https://cran.r-project.org/bin/windows/base/

+++

![image.png](/_static/install_r_img/install_R_win.png)

+++

 * Run the installer

+++

![image.png](/_static/install_r_img/install_R_win2.png)

+++

### MacOS
![image.png](/_static/install_r_img/install_R_mac.png)

+++

 * Run the installer

+++

![image.png](/_static/install_r_img/install_R_mac2.png)

+++

## Step 2 – Install RStudio

RStudio is an open source development environment for R. It adds functionality to make R coding easier and faster.
 * Download the RStudio installer from https://www.rstudio.com/products/rstudio/download/#download (Windows marked in red, use the one below for MacOS.

+++

![image.png](/_static/install_r_img/dl_Rstudio_win.png)

+++

 * Install RStudio (Windows)

+++

![image.png](/_static/install_r_img/install_Rstudio_win.png)

+++

 * Install Rstudio (MacOS)
  ![image.png](/_static/install_r_img/install_Rstudio_mac.png)

+++

## Step 3 – Setup package installation location
 * Open RStudio

+++

![image.png](/_static/install_r_img/code_editor.png)

+++

Packages are additional functions and tools that extend R’s functionality.  They are critical to making full use of R and RStudio.

+++

## Step 4 – Install the packages

You may now run code or commands by typing it into editor and using ``Ctrl+Enter`` to run, or directly into the R console and pressing ``Enter``.

 * The ``install.packages`` command will download and install R packages
 * Packages that require other packages will install all dependencies at once

 * Run ``install.packages(<<package name>>)`` for each of the packages listed above → This will download and install the packages into your library
 * Finally, run the ``library(<<package name>>)`` command to load the library into your R session

You can use the ``sessionInfo()`` command to list out the packages your R session has attached.
