# Development Notes

## Documentation

The documentation web pages can be found in `docs/build/html/`. Please open `index.html` to enter the documentation which provides comprehensive descriptions and working examples for each class and function we provided.

Other than the documentation, `examples/` folder provides some example analysis code for quick-start.

```{note}
The documentation is generated with [Sphinx](https://www.sphinx-doc.org/en/master/index.html). If you are not familiar with it, I would recommend two tutorials for quick-start:

- [A “How to” Guide for Sphinx + ReadTheDocs - sglvladi](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/) provides an easy-to-follow learning curve but omitted some details.
- [Getting Started - Sphinx](https://www.sphinx-doc.org/en/master/usage/quickstart.html) is harder to understand, but provides some essential information to understand the background, which is vital even for very basic configuration.
```

## Project Code

The project code is stored in `pedarProbe/` folder. Under it is a `data/` folder, a default output folder `output/`, a `config/` folder storing configuration variables.

Except for these folders, you must have noticed that there are also some `.py` files, including `parse.py`, `node.py`, `analyse.py`, `export.py`. These are **core modules** for this package:

- {mod}`pedarProbe.parse`
    Loading and parsing pedar plantar pressure data and construct a data node tree for further analysis.
- {mod}`pedarProbe.node`
    Provide well-defined node type for construct the data node tree.
- {mod}`pedarProbe.analyse`
    Provide data analysis functionalities. Short-cut functions are realised in {class}`pedarProbe.node.PedarNode` to facilitate the usability.
- {mod}`pedarProbe.export`
    Provide analysis result export functionalities. Short-cut functions are realised in {class}`pedarProbe.node.PedarNode` to facilitate the usability.

Other than these, there is an `task/` folder haven't been discussed. It's the {mod}`pedarProbe.task` sub-package storing all fine-tuned, twisted analysis features derived from the core modules.

## Version Control

We use `git` as the version control tool, which is very popular among developers and works seamlessly with GitHub. If you are not familiar with it, I would recommend this tutorial for quick-start: [Git Tutorial - Xuefeng Liao](https://www.liaoxuefeng.com/wiki/896043488029600)

Following is a series of notes that summarise major commands:

- [001-Repository Initialisation](https://dynalist.io/d/98jG0ek7Inu6QtMoBTjP4vj6)
- [002-Local Repository Operation](https://dynalist.io/d/4L3UM0yhrYAriHjoQTptEMBk)
- [003-Remote Repository Operation](https://dynalist.io/d/0NozPTssxkVC8aVebCbNmBkR)

## Dependencies

This project is built upon various open-source packages. All dependencies are listed in `requirements.txt`, please install them properly under a Python 3 environment.