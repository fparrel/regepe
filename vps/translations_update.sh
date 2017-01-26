pybabel extract -F babel.cfg -o messages.pot .
pybabel update -i messages.pot -d translations -l fr
pybabel update -i messages.pot -d translations -l es
