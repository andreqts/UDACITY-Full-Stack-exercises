#!/bin/bash
dropdb trivia_test
createdb trivia_test
psql -f trivia.psql -w -q trivia_test
echo "new test database created!"


