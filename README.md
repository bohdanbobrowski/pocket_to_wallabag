# Pocket to wallabag exporter

The original version was written by [gmolveau](https://github.com/gmolveau/pocket_to_wallabag). I cleaned up the code a bit and modified it to meet my requirements, which were to transfer the largest amount of data from Pocket to my Wallabag instance.

This script exports the all links with following values:
- url
- title
- tags (+ adds "pocket")
- status whether the article is archived
- favorite/starred
- language
- all  

Good bye Pocket, hello Wallabag!

## Simplest usage

### 1. Configuration 

Copy `_env_template` as `.env` and fill all values.

### 2. Create environment

    git clone 
    python -m venv venv
    pip install -e .
    