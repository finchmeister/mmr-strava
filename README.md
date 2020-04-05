# MapMyRun to Strava Import

### Requirements:
- Chromedriver
- Pipenv

### Installation

Install requirements:
```
pip install --user pipenv
brew cask install chromedriver
pipenv install
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

```
make delpoy
```