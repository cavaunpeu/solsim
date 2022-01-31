LINE_LENGTH=125

for dir in src tests examples
do
  black $dir --line-length $LINE_LENGTH --check
  flake8 $dir --max-line-length $LINE_LENGTH
done

mypy src/ --config-file mypy.ini --strict