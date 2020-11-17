-----
iobes
-----

.. image:: https://img.shields.io/pypi/v/iobes
    :target: https://pypi.org/project/iobes/
    :alt: PyPI Version
.. image:: https://github.com/blester125/iobes/workflows/Unit%20Test/badge.svg
    :target: https://github.com/blester125/iobes/actions
    :alt: Actions Status    
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code style: black
.. image:: https://readthedocs.org/projects/iobes/badge/?version=latest
    :target: https://iobes.readthedocs.io/en/latest/index.html
    :alt: Documentation Status

A light-weight library for creating span level annotations from token level decisions.

Details and an explaination on *why* you should use this library can be found in the `paper`_ at the Second workshop on Open Source NLP

.. _paper: https://arxiv.org/pdf/2010.04373.pdf

--------
Citation
--------

If you use this library in your research I would appreciate if you would cite the following:

.. code:: BibTex

  @inproceedings{lester-2020-iobes,
      title = "iobes: Library for Span Level Processing",
      author = "Lester, Brian",
      booktitle = "Proceedings of Second Workshop for NLP Open Source Software (NLP-OSS)",
      month = nov,
      year = "2020",
      address = "Online",
      publisher = "Association for Computational Linguistics",
      url = "https://www.aclweb.org/anthology/2020.nlposs-1.16",
      pages = "115--119",
      abstract = "Many tasks in natural language processing, such as named entity recognition and slot-filling, involve identifying and labeling specific spans of text. In order to leverage common models, these tasks are often recast as sequence labeling tasks. Each token is given a label and these labels are prefixed with special tokens such as B- or I-. After a model assigns labels to each token, these prefixes are used to group the tokens into spans. Properly parsing these annotations is critical for producing fair and comparable metrics; however, despite its importance, there is not an easy-to-use, standardized, programmatically integratable library to help work with span labeling. To remedy this, we introduce our open-source library, iobes. iobes is used for parsing, converting, and processing spans represented as token level decisions.",
  }
