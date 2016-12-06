# dota2-messenger-platform
Dota 2 Facebook Messenger

### Information

Dota 2 Facebook Webhooks - Simple query for players information via Facebook messenger.

### Facebook Webhooks Subscription

- [x] messages
- [x] messaging_postbacks

### Facebok App Review for Messenger

- [X] pages_messaging
- [ ] pages_messaging_phone_number
- [ ] pages_messaging_subscriptions

### References

- [Message Platform](https://developers.facebook.com/docs/messenger-platform)


## Programming Language

* Python 3 (tested in 3.5.2)

### Required Packages

* Eve 0.6.4 (include Flask 0.10.1)
* dota2api 1.3.2
* SQLAlchemy 1.1.4
* Flask-SQLAlchemy 2.1
* mysql-connector 2.1.4 (Required for mysqld server, but for other database adapters please read more in this [document](http://docs.sqlalchemy.org/en/latest/dialects/))
* requests 2.12.1

### Optional Packages

* virtualenv 15.1.0
* pip 9.0.1
* gunicorn 19.6.0 (Required and recommended for nginx web server)
* supervisor 3.3.1


## Database

* MySQL 5.7 (tested in 5.7.16)

### Tables

1. Masters
   * heroes: Dota2 Heroes
   * items: Dota2 Items
2. Details
   * match_heroes: Dota2 player matchs with selected hero
   * match_items: Dota2 player matchs with the last used items
3. Analytics
   * match_summaries: Dota2 player statistic
   * match_hero_summaries: Dota2 player heroes statistic
   * match_item_summaries: Dota2 player items statistic
4. Config
   * histories: Records the latest matchs that been processed


## Configuration

File: config.py

### Parameters

* D2_API_KEY: Get one from [Valve](http://dota2api.readthedocs.io/en/latest/tutorial.html).
* CONNECT_STRING: Setup the DBAPI support (example: [mysqld](http://docs.sqlalchemy.org/en/latest/dialects/mysql.html))
* APP_SECRET: Facebook App Secret can be retrieved from the App Dashboard
* PAGE_ACCESS_TOKEN: Get a [Page Access Token](https://developers.facebook.com/docs/messenger-platform/guides/setup#page_access_token)
* VALIDATION_TOKEN: A secured random string for Facebook Webhooks GET validation.  


## How to prepared the database

File: middleware.py

### Methods

* initialize_database(): Creates and checks all the tables in targeted database.
* fill_database_master(): Creates or updates Heroes and Items records.
* fill_database_detail(): Records the next 100 matches since the last match id that been processed and do a analytic to summarize the players statistics.

Note: Dota2 data will be queried from [dota2api](https://dota2api.readthedocs.io/en/latest/) package.

### How to trigger

    python middleware.py


## Concerns

* **Search** function will requires for the players table to be optimized by full-text search.
* Schedulers need to be setup out of this code to re-trigger the **fill_database_master()** and **fill_database_detail()** methods.
* Analytics process need to be improves or re-engineering to use a better solutions to avoid any dirty data because of unexpected errors been raised by the system.

## Private Policy

There will be no data from Facebook Messenger that gonna be recorded inside these application.
