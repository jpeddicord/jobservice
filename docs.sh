#!/bin/sh -e

cd doc
rst2html --stylesheet-path=style.css sls-format-0.8.txt > sls-format-0.8.html
