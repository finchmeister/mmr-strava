PYTHON_EXEC=pipenv run python

sync-latest:
	$(PYTHON_EXEC) download_run.py
	$(PYTHON_EXEC) import_run_strava.py

get-strava-auth:
	$(PYTHON_EXEC) get_strava_auth.py