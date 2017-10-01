import pandas
import webbrowser
from rauth import OAuth1Service

consumer_key = '2272dbdfaffa8158eb3832c5bcd192c2'
consumer_secret = '31ca547ade1bab7f20d22aea8fe0fcd4'
request_token_url = 'https://etws.etrade.com/oauth/request_token'

service = OAuth1Service(
    name='etrade',
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    request_token_url=request_token_url,
    access_token_url = 'https://etws.etrade.com/oauth/access_token',
    authorize_url = 'https://us.etrade.com/e/t/etws/authorize?key={}&token={}',
    base_url = 'https://etws.etrade.com'
)

oauth_token, oauth_token_secret = service.get_request_token(
    params = {
        'oauth_callback': 'oob',
        'format': 'json'}
    )

dir(service)

auth_url = service.authorize_url.format(consumer_key, oauth_token)
webbrowser.open(auth_url)

verifier=raw_input('input verification code\n')

session=service.get_auth_session(
    oauth_token,
    oauth_token_secret,
    params = {'oauth_verifier': verifier}
)

url = 'https://etwssandbox.etrade.com/accounts/sandbox/rest/accountlist.json'
resp = session.get(url)
print(resp)
