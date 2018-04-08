import os
import requests

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"


def _get_csrf(session, cookies):
    """ Get CSRF token for Spotify login. """
    headers = {'user-agent': USER_AGENT}

    response = session.get("https://accounts.spotify.com/login",
                           headers=headers, cookies=cookies)
    response.raise_for_status()

    return response.cookies['csrf_token']


# pylint: disable=too-many-arguments
def _login(session, cookies, username, password, csrf_token):
    """ Logs in with CSRF token and cookie within session. """
    headers = {'user-agent': USER_AGENT}

    data = {"remember": False, "username": username, "password": password,
            "csrf_token": csrf_token}

    response = session.post("https://accounts.spotify.com/api/login",
                            data=data, cookies=cookies, headers=headers)

    response.raise_for_status()


def _get_access_token(session, cookies):
    """ Gets access token after login has been successful. """
    headers = {'user-agent': USER_AGENT}

    response = session.get("https://open.spotify.com/browse",
                           headers=headers, cookies=cookies)
    response.raise_for_status()

    access_token = response.cookies['wp_access_token']

    expiration = response.cookies['wp_expiration']
    expiration_date = int(expiration) // 1000

    return access_token



def start_session(username=None, password=None):
    """ Starts session to get access token. """

    # arbitrary value and can be static
    cookies = {"__bon": "MHwwfC01ODc4MjExMzJ8LTI0Njg4NDg3NTQ0fDF8MXwxfDE="}

    if username is None:
        username = os.getenv("SPOTIFY_USERNAME")

    if password is None:
        password = os.getenv("SPOTIFY_PASS")

    if username is None or password is None:
        raise Exception("No username or password")

    session = requests.Session()
    token = _get_csrf(session, cookies)

    _login(session, cookies, username, password, token)
    access_token = _get_access_token(session, cookies)

    return token