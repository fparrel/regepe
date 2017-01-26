pybabel extract -F babel.cfg -o messages.pot .
pybabel init -i messages.pot -d translations -l fr
pybabel init -i messages.pot -d translations -l es
