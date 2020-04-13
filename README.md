# MapMyRun to Strava Import

Logins into MapMyRun with Selenium, 
downloads the latest unrecognised workout,
then uploads it to Strava

## Local version

### Requirements
- Python 3.7
- Chromedriver
- Pipenv
- Strava client id and secret

### Installation

Install requirements:
```
pip install --user pipenv
brew cask install chromedriver
```

Set environment vars
```
cp .env.dist .env
# Update .env with params
```
Get access token
```
make get-strava-auth
```

### Sync Latest Run


```
make sync-latest
```

## AWS Lambda Version

To run locally
```
make docker-run 
```

To build and deploy to AWS
```
make deploy
```
