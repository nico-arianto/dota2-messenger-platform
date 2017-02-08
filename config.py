dota2api = dict(
    # Get one from Valve (reference: http://dota2api.readthedocs.io/en/latest/tutorial.html)
    D2_API_KEY=''
)

mysql = dict(
    # Setup the DBAPI support (reference: http://docs.sqlalchemy.org/en/latest/dialects/mysql.html)
    CONNECT_STRING='<dialect>+<dbapi>://<username>:<password>@localhost/<database>?unix_socket=/tmp/mysql.sock'
)

facebook = dict(
    URL='https://graph.facebook.com/v2.6/me/messages',
    # App Secret can be retrieved from the App Dashboard
    APP_SECRET='',
    # Get a Page Access Token (reference: https://developers.facebook.com/docs/messenger-platform/guides/setup#page_access_token)
    PAGE_ACCESS_TOKEN=''
)

dota2messenger = dict(
    VALIDATION_TOKEN=''
)
