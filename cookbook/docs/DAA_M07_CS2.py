# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:hydrogen
#     text_representation:
#       extension: .py
#       format_name: hydrogen
#       format_version: '1.3'
#       jupytext_version: 1.11.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown] id="EI2vRNzuiNzd"
# # Py: Customer Sentiment Analysis
# **This notebook was originally created by Michael Storozhev for the Data Analytics Applications subject as *Case study 7.2 - Customer sentiment in travel insurance* in the *DAA M07 Natural language processing* module.**
#
# **Data Analytics Applications is a Fellowship Applications (Module 3) subject with the Actuaries Institute that aims to teach students how to apply a range of data analytics skills, such as neural networks, natural language processing, unsupervised learning and optimisation techniques, together with their professional judgement, to solve a variety of complex and challenging business problems. The business problems used as examples in this subject are drawn from a wide range of industries.**
#
# **Find out more about the course [here](https://www.actuaries.asn.au/education-program/fellowship/subjects-and-syllabus/data-analytics-applications-subject).**
#
# ### Identify the problem
# Businesses often collect feedback from their customers in the form of free-text reviews. This results in businesses receiving very rich but unstructured information about areas where they are meeting their customers’ needs and areas where customers are unsatisfied.
#
# It can be difficult to draw conclusions from this large volume of unstructured data without the help of NLP. The task in this case study is to analyse customer reviews in travel insurance to identify key areas of dissatisfaction. The aim for the business would then be to investigate these areas of discontent so they can improve their future customer service offering.
#
#
# ### Purpose:
# This notebook walks through the use of NLP to analyse customer sentiment to better understand travel insurance related complaints. The objective of the case study is to identify key areas of customer satisfaction (or dissatisfaction) with travel insurance products.
#
# ### References:
# The dataset that is used in this case study was sourced from the Product Review website (https://www.productreview.com.au). ProductReview.com.au is a website devoted to providing consumer opinions on products, services and businesses in Australia.
#
# The dataset for this case study includes 19,395 product reviews in the period May 2017 to August 2020 that relate to travel insurance from 12 different providers.

# %% [markdown] id="zhfHge4GoGma"
# ## Packages
# This section installs packages that will be required for this exercise/case study.
# n.b. for installing ``wordcloud``, if ``pip install wordcloud`` gives an error, try ``conda install -c conda-forge wordcloud``.

# %% colab={"base_uri": "https://localhost:8080/"} id="EcCTrsRthLXG" outputId="9d4c6703-c2d2-4381-ab02-a421e9e7519f"
# Packages for data management.
import pandas as pd
import numpy as np

# Packages to be used in pre-processing the text.
import re
import nltk
nltk.download('stopwords') # For a standard list of stopwords.
nltk.download('wordnet') # For lemmatisation.
import pkg_resources
!pip install symspellpy
from symspellpy import SymSpell, Verbosity

# Packages for visualisation.
# from pprint import pprint
# import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter

# For vectorisation using TF-IDF and t-SNE.
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import TSNE

# For clustering sentences using K-Means clustering.
from sklearn.cluster import KMeans

# For vectorisation using BERT.
!pip install sentence_transformers
from sentence_transformers import SentenceTransformer

# For evaluating the clustering model.
from sklearn.metrics import silhouette_score


# %% [markdown] id="ubusArWzygDW"
# ## Functions
#
# This section defines functions that will be used for this exercise/case study.

# %% id="YmACh9GvuloJ"
# Define a function to clean text.
# Note that not all of these cleaning steps may be needed for different models.
def clean_text(text, full_clean=1):
    ''' Basic cleaning does the following:
        - converts all words to lowercase;
        - removes punctuation and special characters;
        - uses 'split' to create tokens; and
        - fixes spelling mistakes.

        Full cleaning also does the following:
        - removes stop words;
        - performs stemming; and
        - performs lemmatisation.
    '''

    # Convert all text to lower case.
    text = text.lower()

    # Remove all non-digits/non-alphabetical characters ('\w')
    # or  white spaces ('\s').
    text = re.sub(r'[^\w\s]', '', str(text).strip())

    # Create tokens from the text.
    text_list = text.split()

    # Fix spelling mistakes.
    # The sym_spell.lookup function highlights words that are not in the
    # symspell dictionary and offers suggested alternatives for these words.
    text_list_spell = []
    for word in text_list:
        suggestions = sym_spell.lookup(word, Verbosity.CLOSEST, max_edit_distance=3)
        if suggestions:
            text_list_spell.append(suggestions[0].term)
        else:
            pass
    text_list = text_list_spell[:]

    if full_clean==1:
        # Remove stopwords.
        text_list = [word for word in text_list if word not in stopwords]

        # Perform stemming.
        ps = nltk.stem.porter.PorterStemmer()
        text_list = [ps.stem(word) for word in text_list]

        # Perform lemmatisation.
        wnl = nltk.stem.wordnet.WordNetLemmatizer()
        text_list = [wnl.lemmatize(word) for word in text_list]

    result = ' '.join(text_list)
    return result


# %% id="6ZXLdbr5hLXv"
# Define a function to create a word cloud from the words in the dataset.
def get_wordcloud(topic,model,blacklist=[]):

    print('Getting wordcloud for topic {} ...'.format(topic+1))
    body_list = list(dataset['body'][dataset[model] == topic])

    for each in blacklist:
        body_list = [w.replace(each, '') for w in body_list]
    tokens = ' '.join(body_list)
    wordcloud = WordCloud(width=800, height=560,
                          background_color='white', collocations=False,
                          min_font_size=10).generate(tokens)

    # plot the WordCloud image
    plt.figure(figsize=(8, 5.6), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.tight_layout(pad=5)


# %% [markdown] id="SDk8-2xZq0HB"
# ## Data
# This section:
# - imports the data that will be used in the modelling;
# - explores the data; and
# - prepares the data for modelling.

# %% [markdown] id="ZjYEWaxzhLXj"
# ### Import data

# %% colab={"base_uri": "https://localhost:8080/", "height": 93, "resources": {"http://localhost:8080/nbextensions/google.colab/files.js": {"data": "Ly8gQ29weXJpZ2h0IDIwMTcgR29vZ2xlIExMQwovLwovLyBMaWNlbnNlZCB1bmRlciB0aGUgQXBhY2hlIExpY2Vuc2UsIFZlcnNpb24gMi4wICh0aGUgIkxpY2Vuc2UiKTsKLy8geW91IG1heSBub3QgdXNlIHRoaXMgZmlsZSBleGNlcHQgaW4gY29tcGxpYW5jZSB3aXRoIHRoZSBMaWNlbnNlLgovLyBZb3UgbWF5IG9idGFpbiBhIGNvcHkgb2YgdGhlIExpY2Vuc2UgYXQKLy8KLy8gICAgICBodHRwOi8vd3d3LmFwYWNoZS5vcmcvbGljZW5zZXMvTElDRU5TRS0yLjAKLy8KLy8gVW5sZXNzIHJlcXVpcmVkIGJ5IGFwcGxpY2FibGUgbGF3IG9yIGFncmVlZCB0byBpbiB3cml0aW5nLCBzb2Z0d2FyZQovLyBkaXN0cmlidXRlZCB1bmRlciB0aGUgTGljZW5zZSBpcyBkaXN0cmlidXRlZCBvbiBhbiAiQVMgSVMiIEJBU0lTLAovLyBXSVRIT1VUIFdBUlJBTlRJRVMgT1IgQ09ORElUSU9OUyBPRiBBTlkgS0lORCwgZWl0aGVyIGV4cHJlc3Mgb3IgaW1wbGllZC4KLy8gU2VlIHRoZSBMaWNlbnNlIGZvciB0aGUgc3BlY2lmaWMgbGFuZ3VhZ2UgZ292ZXJuaW5nIHBlcm1pc3Npb25zIGFuZAovLyBsaW1pdGF0aW9ucyB1bmRlciB0aGUgTGljZW5zZS4KCi8qKgogKiBAZmlsZW92ZXJ2aWV3IEhlbHBlcnMgZm9yIGdvb2dsZS5jb2xhYiBQeXRob24gbW9kdWxlLgogKi8KKGZ1bmN0aW9uKHNjb3BlKSB7CmZ1bmN0aW9uIHNwYW4odGV4dCwgc3R5bGVBdHRyaWJ1dGVzID0ge30pIHsKICBjb25zdCBlbGVtZW50ID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgnc3BhbicpOwogIGVsZW1lbnQudGV4dENvbnRlbnQgPSB0ZXh0OwogIGZvciAoY29uc3Qga2V5IG9mIE9iamVjdC5rZXlzKHN0eWxlQXR0cmlidXRlcykpIHsKICAgIGVsZW1lbnQuc3R5bGVba2V5XSA9IHN0eWxlQXR0cmlidXRlc1trZXldOwogIH0KICByZXR1cm4gZWxlbWVudDsKfQoKLy8gTWF4IG51bWJlciBvZiBieXRlcyB3aGljaCB3aWxsIGJlIHVwbG9hZGVkIGF0IGEgdGltZS4KY29uc3QgTUFYX1BBWUxPQURfU0laRSA9IDEwMCAqIDEwMjQ7CgpmdW5jdGlvbiBfdXBsb2FkRmlsZXMoaW5wdXRJZCwgb3V0cHV0SWQpIHsKICBjb25zdCBzdGVwcyA9IHVwbG9hZEZpbGVzU3RlcChpbnB1dElkLCBvdXRwdXRJZCk7CiAgY29uc3Qgb3V0cHV0RWxlbWVudCA9IGRvY3VtZW50LmdldEVsZW1lbnRCeUlkKG91dHB1dElkKTsKICAvLyBDYWNoZSBzdGVwcyBvbiB0aGUgb3V0cHV0RWxlbWVudCB0byBtYWtlIGl0IGF2YWlsYWJsZSBmb3IgdGhlIG5leHQgY2FsbAogIC8vIHRvIHVwbG9hZEZpbGVzQ29udGludWUgZnJvbSBQeXRob24uCiAgb3V0cHV0RWxlbWVudC5zdGVwcyA9IHN0ZXBzOwoKICByZXR1cm4gX3VwbG9hZEZpbGVzQ29udGludWUob3V0cHV0SWQpOwp9CgovLyBUaGlzIGlzIHJvdWdobHkgYW4gYXN5bmMgZ2VuZXJhdG9yIChub3Qgc3VwcG9ydGVkIGluIHRoZSBicm93c2VyIHlldCksCi8vIHdoZXJlIHRoZXJlIGFyZSBtdWx0aXBsZSBhc3luY2hyb25vdXMgc3RlcHMgYW5kIHRoZSBQeXRob24gc2lkZSBpcyBnb2luZwovLyB0byBwb2xsIGZvciBjb21wbGV0aW9uIG9mIGVhY2ggc3RlcC4KLy8gVGhpcyB1c2VzIGEgUHJvbWlzZSB0byBibG9jayB0aGUgcHl0aG9uIHNpZGUgb24gY29tcGxldGlvbiBvZiBlYWNoIHN0ZXAsCi8vIHRoZW4gcGFzc2VzIHRoZSByZXN1bHQgb2YgdGhlIHByZXZpb3VzIHN0ZXAgYXMgdGhlIGlucHV0IHRvIHRoZSBuZXh0IHN0ZXAuCmZ1bmN0aW9uIF91cGxvYWRGaWxlc0NvbnRpbnVlKG91dHB1dElkKSB7CiAgY29uc3Qgb3V0cHV0RWxlbWVudCA9IGRvY3VtZW50LmdldEVsZW1lbnRCeUlkKG91dHB1dElkKTsKICBjb25zdCBzdGVwcyA9IG91dHB1dEVsZW1lbnQuc3RlcHM7CgogIGNvbnN0IG5leHQgPSBzdGVwcy5uZXh0KG91dHB1dEVsZW1lbnQubGFzdFByb21pc2VWYWx1ZSk7CiAgcmV0dXJuIFByb21pc2UucmVzb2x2ZShuZXh0LnZhbHVlLnByb21pc2UpLnRoZW4oKHZhbHVlKSA9PiB7CiAgICAvLyBDYWNoZSB0aGUgbGFzdCBwcm9taXNlIHZhbHVlIHRvIG1ha2UgaXQgYXZhaWxhYmxlIHRvIHRoZSBuZXh0CiAgICAvLyBzdGVwIG9mIHRoZSBnZW5lcmF0b3IuCiAgICBvdXRwdXRFbGVtZW50Lmxhc3RQcm9taXNlVmFsdWUgPSB2YWx1ZTsKICAgIHJldHVybiBuZXh0LnZhbHVlLnJlc3BvbnNlOwogIH0pOwp9CgovKioKICogR2VuZXJhdG9yIGZ1bmN0aW9uIHdoaWNoIGlzIGNhbGxlZCBiZXR3ZWVuIGVhY2ggYXN5bmMgc3RlcCBvZiB0aGUgdXBsb2FkCiAqIHByb2Nlc3MuCiAqIEBwYXJhbSB7c3RyaW5nfSBpbnB1dElkIEVsZW1lbnQgSUQgb2YgdGhlIGlucHV0IGZpbGUgcGlja2VyIGVsZW1lbnQuCiAqIEBwYXJhbSB7c3RyaW5nfSBvdXRwdXRJZCBFbGVtZW50IElEIG9mIHRoZSBvdXRwdXQgZGlzcGxheS4KICogQHJldHVybiB7IUl0ZXJhYmxlPCFPYmplY3Q+fSBJdGVyYWJsZSBvZiBuZXh0IHN0ZXBzLgogKi8KZnVuY3Rpb24qIHVwbG9hZEZpbGVzU3RlcChpbnB1dElkLCBvdXRwdXRJZCkgewogIGNvbnN0IGlucHV0RWxlbWVudCA9IGRvY3VtZW50LmdldEVsZW1lbnRCeUlkKGlucHV0SWQpOwogIGlucHV0RWxlbWVudC5kaXNhYmxlZCA9IGZhbHNlOwoKICBjb25zdCBvdXRwdXRFbGVtZW50ID0gZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQob3V0cHV0SWQpOwogIG91dHB1dEVsZW1lbnQuaW5uZXJIVE1MID0gJyc7CgogIGNvbnN0IHBpY2tlZFByb21pc2UgPSBuZXcgUHJvbWlzZSgocmVzb2x2ZSkgPT4gewogICAgaW5wdXRFbGVtZW50LmFkZEV2ZW50TGlzdGVuZXIoJ2NoYW5nZScsIChlKSA9PiB7CiAgICAgIHJlc29sdmUoZS50YXJnZXQuZmlsZXMpOwogICAgfSk7CiAgfSk7CgogIGNvbnN0IGNhbmNlbCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoJ2J1dHRvbicpOwogIGlucHV0RWxlbWVudC5wYXJlbnRFbGVtZW50LmFwcGVuZENoaWxkKGNhbmNlbCk7CiAgY2FuY2VsLnRleHRDb250ZW50ID0gJ0NhbmNlbCB1cGxvYWQnOwogIGNvbnN0IGNhbmNlbFByb21pc2UgPSBuZXcgUHJvbWlzZSgocmVzb2x2ZSkgPT4gewogICAgY2FuY2VsLm9uY2xpY2sgPSAoKSA9PiB7CiAgICAgIHJlc29sdmUobnVsbCk7CiAgICB9OwogIH0pOwoKICAvLyBXYWl0IGZvciB0aGUgdXNlciB0byBwaWNrIHRoZSBmaWxlcy4KICBjb25zdCBmaWxlcyA9IHlpZWxkIHsKICAgIHByb21pc2U6IFByb21pc2UucmFjZShbcGlja2VkUHJvbWlzZSwgY2FuY2VsUHJvbWlzZV0pLAogICAgcmVzcG9uc2U6IHsKICAgICAgYWN0aW9uOiAnc3RhcnRpbmcnLAogICAgfQogIH07CgogIGNhbmNlbC5yZW1vdmUoKTsKCiAgLy8gRGlzYWJsZSB0aGUgaW5wdXQgZWxlbWVudCBzaW5jZSBmdXJ0aGVyIHBpY2tzIGFyZSBub3QgYWxsb3dlZC4KICBpbnB1dEVsZW1lbnQuZGlzYWJsZWQgPSB0cnVlOwoKICBpZiAoIWZpbGVzKSB7CiAgICByZXR1cm4gewogICAgICByZXNwb25zZTogewogICAgICAgIGFjdGlvbjogJ2NvbXBsZXRlJywKICAgICAgfQogICAgfTsKICB9CgogIGZvciAoY29uc3QgZmlsZSBvZiBmaWxlcykgewogICAgY29uc3QgbGkgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCdsaScpOwogICAgbGkuYXBwZW5kKHNwYW4oZmlsZS5uYW1lLCB7Zm9udFdlaWdodDogJ2JvbGQnfSkpOwogICAgbGkuYXBwZW5kKHNwYW4oCiAgICAgICAgYCgke2ZpbGUudHlwZSB8fCAnbi9hJ30pIC0gJHtmaWxlLnNpemV9IGJ5dGVzLCBgICsKICAgICAgICBgbGFzdCBtb2RpZmllZDogJHsKICAgICAgICAgICAgZmlsZS5sYXN0TW9kaWZpZWREYXRlID8gZmlsZS5sYXN0TW9kaWZpZWREYXRlLnRvTG9jYWxlRGF0ZVN0cmluZygpIDoKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgJ24vYSd9IC0gYCkpOwogICAgY29uc3QgcGVyY2VudCA9IHNwYW4oJzAlIGRvbmUnKTsKICAgIGxpLmFwcGVuZENoaWxkKHBlcmNlbnQpOwoKICAgIG91dHB1dEVsZW1lbnQuYXBwZW5kQ2hpbGQobGkpOwoKICAgIGNvbnN0IGZpbGVEYXRhUHJvbWlzZSA9IG5ldyBQcm9taXNlKChyZXNvbHZlKSA9PiB7CiAgICAgIGNvbnN0IHJlYWRlciA9IG5ldyBGaWxlUmVhZGVyKCk7CiAgICAgIHJlYWRlci5vbmxvYWQgPSAoZSkgPT4gewogICAgICAgIHJlc29sdmUoZS50YXJnZXQucmVzdWx0KTsKICAgICAgfTsKICAgICAgcmVhZGVyLnJlYWRBc0FycmF5QnVmZmVyKGZpbGUpOwogICAgfSk7CiAgICAvLyBXYWl0IGZvciB0aGUgZGF0YSB0byBiZSByZWFkeS4KICAgIGxldCBmaWxlRGF0YSA9IHlpZWxkIHsKICAgICAgcHJvbWlzZTogZmlsZURhdGFQcm9taXNlLAogICAgICByZXNwb25zZTogewogICAgICAgIGFjdGlvbjogJ2NvbnRpbnVlJywKICAgICAgfQogICAgfTsKCiAgICAvLyBVc2UgYSBjaHVua2VkIHNlbmRpbmcgdG8gYXZvaWQgbWVzc2FnZSBzaXplIGxpbWl0cy4gU2VlIGIvNjIxMTU2NjAuCiAgICBsZXQgcG9zaXRpb24gPSAwOwogICAgZG8gewogICAgICBjb25zdCBsZW5ndGggPSBNYXRoLm1pbihmaWxlRGF0YS5ieXRlTGVuZ3RoIC0gcG9zaXRpb24sIE1BWF9QQVlMT0FEX1NJWkUpOwogICAgICBjb25zdCBjaHVuayA9IG5ldyBVaW50OEFycmF5KGZpbGVEYXRhLCBwb3NpdGlvbiwgbGVuZ3RoKTsKICAgICAgcG9zaXRpb24gKz0gbGVuZ3RoOwoKICAgICAgY29uc3QgYmFzZTY0ID0gYnRvYShTdHJpbmcuZnJvbUNoYXJDb2RlLmFwcGx5KG51bGwsIGNodW5rKSk7CiAgICAgIHlpZWxkIHsKICAgICAgICByZXNwb25zZTogewogICAgICAgICAgYWN0aW9uOiAnYXBwZW5kJywKICAgICAgICAgIGZpbGU6IGZpbGUubmFtZSwKICAgICAgICAgIGRhdGE6IGJhc2U2NCwKICAgICAgICB9LAogICAgICB9OwoKICAgICAgbGV0IHBlcmNlbnREb25lID0gZmlsZURhdGEuYnl0ZUxlbmd0aCA9PT0gMCA/CiAgICAgICAgICAxMDAgOgogICAgICAgICAgTWF0aC5yb3VuZCgocG9zaXRpb24gLyBmaWxlRGF0YS5ieXRlTGVuZ3RoKSAqIDEwMCk7CiAgICAgIHBlcmNlbnQudGV4dENvbnRlbnQgPSBgJHtwZXJjZW50RG9uZX0lIGRvbmVgOwoKICAgIH0gd2hpbGUgKHBvc2l0aW9uIDwgZmlsZURhdGEuYnl0ZUxlbmd0aCk7CiAgfQoKICAvLyBBbGwgZG9uZS4KICB5aWVsZCB7CiAgICByZXNwb25zZTogewogICAgICBhY3Rpb246ICdjb21wbGV0ZScsCiAgICB9CiAgfTsKfQoKc2NvcGUuZ29vZ2xlID0gc2NvcGUuZ29vZ2xlIHx8IHt9OwpzY29wZS5nb29nbGUuY29sYWIgPSBzY29wZS5nb29nbGUuY29sYWIgfHwge307CnNjb3BlLmdvb2dsZS5jb2xhYi5fZmlsZXMgPSB7CiAgX3VwbG9hZEZpbGVzLAogIF91cGxvYWRGaWxlc0NvbnRpbnVlLAp9Owp9KShzZWxmKTsK", "headers": [["content-type", "application/javascript"]], "ok": true, "status": 200, "status_text": "OK"}}} id="zRz4nlQyhLXk" outputId="304f68bc-2cf9-4fd0-888c-4895c85d8fef"
# Create dataset from the csv import.
dataset = pd.read_csv(
    'https://actuariesinstitute.github.io/cookbook/_static/daa_datasets/DAA_M07_CS2_data.csv.zip',
    encoding='cp1252')
print(dataset.shape)

# %% colab={"base_uri": "https://localhost:8080/"} id="TQ74oyZehLXU" outputId="45762004-2554-43b5-83b2-148731e35c58"
# Get spelling datasets.
sym_spell = SymSpell(max_dictionary_edit_distance=3, prefix_length=7)
dictionary_path = pkg_resources.resource_filename('symspellpy', 'frequency_dictionary_en_82_765.txt')
sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)

# Add some common words to the dictionary that are likely to be found in the
# case study corpus, to avoid them being incorrectly 'fixed' by the spell checker.
sym_spell.create_dictionary_entry('covid', 5)
sym_spell.create_dictionary_entry('coronavirus', 5)

# %% [markdown] id="4qC9iRUytyeN"
# ### Explore data (EDA)

# %% colab={"base_uri": "https://localhost:8080/"} id="7c1NGfW1eeZ0" outputId="6c163ca9-bd82-49b9-f0a1-971644fad037"
# View the features of the dataset.
print(dataset.columns)

# %% colab={"base_uri": "https://localhost:8080/"} id="4pmZbne2hQst" outputId="1be9a6be-01d6-4ba4-f3b3-9e65c156d45e"
# Check the size of the dataset.
print(dataset.shape)

# %% colab={"base_uri": "https://localhost:8080/", "height": 72} id="h3-yRhU9hLXm" outputId="9329652d-c0ee-4ed5-e9dc-78f0d7a471e3"
# Print the text of the first review.
dataset['body'][0]

# %% [markdown] id="bw_tRackuJd9"
# ### Prepare data
#
# This section involves cleaning the data to prepare it for analysis. The following cleaning steps are taken:
# - convert all words to lowercase;
# - remove punctuation and special characters;
# - use 'split' to create tokens;
# - fix spelling mistakes;
# - remove stop words (when doing a full clean);
# - perform stemming (when doing a full clean); and
# - perform lemmatisation (when doing a full clean).

# %% [markdown] id="nhQdmavQDT2w"
# #### Clean data

# %% id="FvlUmDJNhLXo"
# Get stopwords.
stopwords = nltk.corpus.stopwords.words('english')

# %% colab={"base_uri": "https://localhost:8080/"} id="nexbwJcJhLXs" outputId="4d688fb0-724a-41a9-ff53-fbeee42b6a71"
# Check that the cleaning function defined at the top of the notebook
# is working as expected.
review_number = 11
print('--Original')
print(dataset['body'][review_number-1])
print('\n')
print('--Basic clean')
print(clean_text(dataset['body'][review_number-1], full_clean=0))
print('\n')
print('--Full clean')
print(clean_text(dataset['body'][review_number-1], full_clean=1))

# %% [markdown] id="IigCJhPPxXyA"
# In the above example, take note of what the cleaning process did to the following words:
# - 'eveyhing' was corrected to 'everything' by the spell-checker;
# - 'pre-exsisting' was corrected to 'preexisting' by the spell-checker;
# - 'gastro' was corrected to 'castro' by the spell-checker; and
# - 'please' was converted to 'plea' by the stemmer and/or the lemmatiser.
#
# Do all of these changes make sense?
#
# You should look at the cleaning output for a few different reviews to find other examples of changes that have been made by the cleaning function. Are you happy with all of these changes?

# %% colab={"base_uri": "https://localhost:8080/", "height": 293} id="NgKAP1_ThLXt" outputId="b28f6f88-2556-4566-8037-2a187df64827"
# Run the cleaning function on the full dataset. This step can take a while to run.
dataset['body_clean_full'] = dataset['body'].apply(lambda x: clean_text(x, full_clean=1))
    # The lambda function is used above to apply the clean_text function to all the
    # reviews in the corpus.
dataset['body_clean_bert'] = dataset['body'].apply(lambda x: clean_text(x, full_clean=0))
    # The 'body_clean_bert' uses a basic clean to prepare the data for use with the
    # Bert model.
dataset.head()

# %% [markdown] id="19TTnnckqK-u"
# #### Subset data
# This section allows you to subset the data to be used in the analysis. For example, you might choose a subset of the entire date range, or you might choose to review only observations with a certain rating.

# %% id="SiDqkPRcgP7v"
# Set date range of reviews to be analysed.

Months = ['2019-01','2019-02','2019-03','2019-04','2019-05','2019-06',
          '2019-07','2019-08','2019-09','2019-10','2019-11','2019-12',
          '2020-01','2020-02','2020-03','2020-04','2020-05','2020-06']
          # Because 'pubMonth' is recorded as a string, a list of
          # string values is created, representing the months of
          # interest for this analysis.
          # An alternative approach would be to convert the 'pubDate' into
          # a date and search within a specified date range.

# Choose which reviews, based on rating, will be included in the analysis.
# In this case, the focus will be on reviews with a low rating of 1 or 2,
# to try to understand what makes customers complain about travel insurance.

ratings = [1,2]

# If you want to apply the subsetting specified above, then remove the '#'
# at the start of each line below:

# dataset = dataset[dataset['pubMonth'].isin(Months)]
# dataset = dataset[dataset['rating'].isin(ratings)]
# print(dataset.shape)

# %% [markdown] id="xq-g12qpDYHr"
# #### Vectorise
# Two vectorisation approaches are used below:
# - approach 1 uses TF-IDF; and
# - approach 2 uses BERT.

# %% [markdown] id="m0oRRWoQhLXw"
# ##### TF-IDF
#
# In this approach, TF-IDF is used to get the statistical weights of the tokens in each review. These weights are then reduced to two dimensions using t-SNE (t-SNE is an alternative dimension reduction technique to PCA). This makes it easier to visualise the different clusters that are found using K-Means clustering (see the Modelling section of the notebook).

# %% colab={"base_uri": "https://localhost:8080/"} id="hYghYBfLhLXx" outputId="dd963dc7-dc76-48f5-e221-32af9e6c3056"
# Generate TF-IDF weights
clean_input = dataset['body_clean_full'].tolist()
tfidf = TfidfVectorizer()
embedding_tfidf = tfidf.fit_transform(clean_input)
print('Shape of list containing reviews and their tf-idf weights:', embedding_tfidf.shape)

tsne1 = TSNE(n_components=2)
embedding_tfidf_tsne = tsne1.fit_transform(embedding_tfidf)
print('Shape of list containing reviews and their t-SNE components:', embedding_tfidf_tsne.shape)

# %% [markdown] id="SWJRP2_mhLX1"
# ##### BERT
#
# This approach uses BERT to get the encodings for each review. These weights are then again reduced to two dimensions using t-SNE to make it easier to visualise the different clusters that are found using K-Means clustering.
#
#
# Import the BERT data set (the text that has only had basic cleaning).

# %% id="SWJRP2_mhLX1"
bert_input = dataset['body_clean_bert'].tolist()
print('Getting vector embeddings for BERT ...')

# %% [markdown] id="SWJRP2_mhLX1"
# Create a model to perform embeddings using BERT.

# %% id="SWJRP2_mhLX1"
model = SentenceTransformer('distilbert-base-nli-mean-tokens')

# %% [markdown] id="SWJRP2_mhLX1"
# Perform the embeddings.
# Note that the first time this is run, the BERT model will download.
# This can take some time as the model is approximately 265Mb.

# %% id="SWJRP2_mhLX1"
embeddings = model.encode(bert_input, show_progress_bar=False)
embedding_BERT = np.array(embeddings)

print('Getting vector embeddings for BERT. Done!')

print('Shape of list containing reviews and their BERT weights:', embeddings.shape)

# %% [markdown] id="SWJRP2_mhLX1"
# Again, t-SNE is applied to reduce the dimension of the BERT embeddings.

# %% id="SWJRP2_mhLX1"
tsne2 = TSNE(n_components=2)
embedding_BERT_tsne = tsne2.fit_transform(embedding_BERT)
print('Shape of list containing reviews and their t-SNE components:',
      embedding_BERT_tsne.shape)

# %% colab={"base_uri": "https://localhost:8080/"} id="1FapMWUJhLX3" outputId="a734cf41-6253-4e81-af8f-6bb240333f42"
# Print an example of a BERT embedding.
print('Bert embedding sample', embeddings[0][0:50])
  # This prints the first 50 vectors created by the BERT
  # embedding for the first review in the dataset.

# %% [markdown] id="HPcMEcsaFq5n"
# ## Modelling
# This section uses the vectorised reviews to perform topic modelling. This allows the reviews to be clustered into different topics, to identify the main themes that emerge from the reviews.

# %% [markdown] id="4SmNY560Ut4p"
# #### Using TF-IDF vectorisation

# %% colab={"base_uri": "https://localhost:8080/"} id="xsfU8fORF5rl" outputId="029b85ee-719e-4944-f812-01a907634cfb"
# Use the TF-IDF approach to cluster the reviews into K topics.
K = 6
kmeans_model1 = KMeans(K)
score_tfidf_tsne = kmeans_model1.fit(embedding_tfidf_tsne).score(embedding_tfidf_tsne)
    # This step fits the kmeans model and calculates a cluster score (WCSS)
    # for the model. WCSS measures the (negative) sum of squared distances
    # of observations to their closest cluster centroid, so a smaller score
    # indicates a better clustering of the data.
labels_tfidf_kmeans = kmeans_model1.predict(embedding_tfidf_tsne)
dataset['label_TFIDF_KMeans'] = list(labels_tfidf_kmeans)
print(score_tfidf_tsne)

# %% colab={"base_uri": "https://localhost:8080/", "height": 1000} id="RL4By8czhLXy" outputId="70deae02-399a-47a9-cae2-78617ae54a26"
# Create a set of distinct labels from the clustering.
labels1 = np.array(labels_tfidf_kmeans)
distinct_labels1 =  set(labels_tfidf_kmeans)

# Create a plot of the reviews clustered by 'topic'.
# Note that at this point the 'topic' of each cluster has not yet
# been analysed or defined.
n = len(labels_tfidf_kmeans)
counter = Counter(labels1)
for i in range(len(distinct_labels1)):
    ratio = (counter[i] / n )* 100
    cluster_label = f'cluster {i+1}: { round(ratio,2)}'
    x = embedding_tfidf_tsne[:, 0][labels1 == i]
    y = embedding_tfidf_tsne[:, 1][labels1 == i]
    plt.plot(x, y, '.', alpha=0.4, label= cluster_label)
plt.legend(title='Topic',loc = 'upper left', bbox_to_anchor=(1.01,1))
plt.title('{} topics identified with tf-idf, t-SNE and KMeans'.format(K))

# Create a list of context specific common words that will
# be hidden in the word clouds produced.
hidden_words = ['insurance','travel','policy','claim']

# Create a word cloud to help identify the meaning of
# each 'topic' identified in the KMeans clustering.
for each in range(0,K):
    get_wordcloud(each,'label_TFIDF_KMeans',hidden_words)


# %% [markdown] id="PZ9m9ImsU1iF"
# ### Using BERT vectorisation

# %% colab={"base_uri": "https://localhost:8080/"} id="FiMi5anKhLX4" outputId="6f2bf401-099d-4806-a9bd-d6a4b861c681"
# Apply K-Means clustering to the BERT vectors.
K2 = 6
kmeans_model2 = KMeans(K2)
score_BERT_tsne = kmeans_model2.fit(embedding_BERT_tsne).score(embedding_BERT_tsne)
labels_BERT_kmeans = kmeans_model2.predict(embedding_BERT_tsne)
dataset['label_BERT_KMeans'] = list(labels_BERT_kmeans)
print(score_BERT_tsne)

# %% colab={"base_uri": "https://localhost:8080/", "height": 1000} id="b7dVxc-eZNzj" outputId="74720684-988a-4fcd-89d5-c29109cba412"
# Create a set of distinct labels from the clustering.
labels2 = np.array(labels_BERT_kmeans)
distinct_labels2 =  set(labels_BERT_kmeans)

# Create a plot of the reviews clustered by 'topic'
# where the 'topic' of each cluster has not yet
# been analysed.
n = len(embedding_BERT_tsne)
counter = Counter(labels2)
for i in range(len(distinct_labels2)):
    ratio = (counter[i] / n )* 100
    cluster_label = f'cluster {i+1}: { round(ratio,2)}'
    x = embedding_BERT_tsne[:, 0][labels2 == i]
    y = embedding_BERT_tsne[:, 1][labels2 == i]
    plt.plot(x, y, '.', alpha=0.4, label= cluster_label)
plt.legend(title='Topic',loc = 'upper left', bbox_to_anchor=(1.01,1))
plt.title('{} topics identified with BERT, tf-idf and t-SNE'.format(K2))

# Create a list of context specific common words that will
# be hidden in the word clouds producted.
hidden_words2 = ['insurance','travel','policy','claim']

# Create a word cloud to help identify the meaning of
# each 'topic' identified in the KMeans clustering.
for each in range(0,K2):
    get_wordcloud(each,'label_BERT_KMeans',hidden_words2)

# %% [markdown] id="bDt1DBATWJ_3"
# ## Evaluate
# This section performs some evaluation of the topic modelling using TF-IDF and BERT.
#
# The metric used below is the 'silhouette value' which is a measure of how similar observations are to their own cluster compared to other clusters. This is an alternative evaluation measure to those presented in Module 7.
#
# The best silhouette value is 1 and the worst value is -1. Values near 0 indicate overlapping clusters. Negative values generally indicate that an observation has been assigned to the wrong cluster, as a different cluster is more similar.

# %% colab={"base_uri": "https://localhost:8080/"} id="YvZz_a-DhLX5" outputId="df75bfdf-cec6-4639-e361-6537f5e1108a"
# Calculate the silhouette value for the TF-IDF based clustering after t-SNE
# has been applied to reduce the dimension of the embeddings.
print('Silhouette Score (TF-IDF and t-SNE):',
      silhouette_score(embedding_tfidf_tsne , labels_tfidf_kmeans))

# Calculate silhouette values for the BERT based clustering.
#print('Silhouette Score (BERT):',
#      silhouette_score(embedding_BERT , labels_BERT_kmeans))

# Calculate the silhouette value for the BERT based clustering after t-SNE
# has been applied to reduce the dimension of the embeddings.
print('Silhouette Score (BERT and t-SNE):',
      silhouette_score(embedding_BERT_tsne , labels_BERT_kmeans))

# The WCSS scores for the TF-IDF and BERT models are also shown:
print('WCSS Score (TF-IDF and t-SNE):', score_tfidf_tsne)
print('WCSS Score (BERT):', score_BERT_tsne)

# %% [markdown] id="rcGglcOCcU5C"
# The output above suggests that the embeddings using BERT produced marginally better clustering outcomes, with a slightly higher silhouette value and WCSS score.

# %% [markdown] id="LKZDsrkUc1KY"
# # Commentary
# The 'Monitor results' section of Case Study 2 in Module 6 of the DAA course contained a discussion of how the analysis such as that conducted above can be used to interpret key areas or themes of feedback from travel insurance customers.
#
# The reader can play around with analysing different subsets of the reviews in this case study, to see what themes emerge for reviews with high and low ratings, and for reviews over different time periods.
