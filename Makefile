.PHONY: sync-latest get-strava-auth help check clean fetch-dependencies docker-build build-lambda-package update-function-code

PYTHON_EXEC=pipenv run python

sync-latest:		## Imports most recent run
	$(PYTHON_EXEC) download_run.py
	$(PYTHON_EXEC) import_run_strava.py

get-strava-auth:		## Gets the Strava Oauth credentials
	$(PYTHON_EXEC) get_strava_auth.py

clean:		## delete pycache, build files
	@rm -rf build build.zip
	@rm -rf __pycache__

fetch-dependencies:		## download chromedriver, headless-chrome to `./bin/`
	@mkdir -p bin/

	# Get chromedriver
	curl -SL https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip > chromedriver.zip
	unzip chromedriver.zip -d bin/

	# Get Headless-chrome
	curl -SL https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-37/stable-headless-chromium-amazonlinux-2017-03.zip > headless-chromium.zip
	unzip headless-chromium.zip -d bin/

	# Clean
	@rm headless-chromium.zip chromedriver.zip

docker-build:		## create Docker image
	docker-compose build

docker-run:			## run `src.lambda_function.lambda_handler` with docker-compose
	docker-compose run lambda src.lambda_function.lambda_handler

build-lambda-package: clean		## prepares zip archive for AWS Lambda deploy (-> build/build.zip)
	mkdir build
	cp -r src build/.
	cp -r bin build/.
	cp -r lib build/.
	pip install -r requirements.txt -t build/lib/.
	rm -rf build/lib/pyarrow build/lib/numpy build/lib/pandas
	cd build; zip -9qr build.zip .
	cp build/build.zip .
	rm -rf build

deploy: build-lambda-package    ## Builds and deploys AWS Lambda
	aws s3 cp build.zip s3://mmr-strava-sync-data
	aws lambda update-function-code --function-name=mmr-strava-sync --s3-bucket=mmr-strava-sync-data --s3-key=build.zip | cat

help:
	@python -c 'import fileinput,re; \
	ms=filter(None, (re.search("([a-zA-Z_-]+):.*?## (.*)$$",l) for l in fileinput.input())); \
	print("\n".join(sorted("\033[36m  {:25}\033[0m {}".format(*m.groups()) for m in ms)))' $(MAKEFILE_LIST)