from stravaio import *


def strava_oauth2(client_id=None, client_secret=None):
    port = 8000
    _request_strava_authorize(client_id, port)
    logger.info(f"serving at port {port}")
    token = run_server_and_wait_for_token(
        port=port,
        client_id=client_id,
        client_secret=client_secret
    )

    return token


def _request_strava_authorize(client_id, port):
    params_oauth = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": f"http://localhost:{port}/authorization_successful",
        "scope": "read,profile:read_all,activity:read,activity:write",
        "state": 'https://github.com/finchmeister/strava-http',
        "approval_prompt": "force"
    }
    values_url = urllib.parse.urlencode(params_oauth)
    base_url = 'https://www.strava.com/oauth/authorize'
    rv = base_url + '?' + values_url
    print(rv)
    webbrowser.get().open(rv)
    return None


def main():
    auth_data = strava_oauth2(
        client_id=os.getenv('STRAVA_CLIENT_ID', None),
        client_secret=os.getenv('STRAVA_CLIENT_SECRET', None)
    )

    with open('strava_auth.json', 'w') as outfile:
        json.dump(auth_data, outfile)


if __name__ == "__main__":
    main()
