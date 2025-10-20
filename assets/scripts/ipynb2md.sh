prefix=$1

jupyter nbconvert --to markdown $prefix.ipynb --TemplateExporter.exclude_input=False --output $prefix.md