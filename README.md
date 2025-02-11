# Pocket to wallabag exporter

The original version was written by [gmolveau](https://github.com/gmolveau/pocket_to_wallabag). I cleaned up the code a bit and modified it to meet my requirements, which were to transfer the largest amount of data from Pocket to my Wallabag instance.

This script exports the all links with following values:
- url
- title
- tags (+ adds "pocket")
- status whether the article is archived
- favorite/starred
- language

## Simplest usage

### 1. Configuration 

Copy `_env_template` as `.env` and fill all values.

### 2. Clone repository

    git clone git@github.com:bohdanbobrowski/pocket_to_wallabag.git
    cd pocket_to_wallabag

### 3. Create environment

    python -m venv venv

...and the on Linux/macOS:

    source venv/bin/activate
    source .env

...on Windows:

    venv/Scripts/activate
    set_env

...and finally:

    pip install -e .

### 4. Run

    pocket_to_wallabag

### Good bye Pocket, hello Wallabag!
   
