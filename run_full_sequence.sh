#!/bin/bash
python manage.py pull_new_docs
./parse_files.sh
python manage.py add_new_docs
python manage.py update_index
python manage.py mark_indexed
