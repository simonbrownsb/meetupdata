# meetupdata

Summary
-------

This utility fetches data from a limited subset of the meetup.com API.

It can be used to fetch information about the following entities:

  - members (of a group)
  - past-events (of a group - but it only works for certain groups)
  - future-events (of a group - but it only works for certain groups)
  - attendance (of a single past event for a group)
  - activity (of all groups you are a member of)

The full meetup API is much richer and provides a whole lot more entities,
and much more ability to filter and scroll results, but this simple wrapper
just uses a small subset of that API.

Usage:

    python meetup_data.py [FLAGS] ACCESS_TOKEN ENTITY [PARAMS]

The PARAMS depend on what ENTITY is being used.  See the Entities section
below (or run it with -h to get full help description).

It writes output to standard output, in either CSV or JSON format. It's CSV
by default, unless you use the --json flag.

You should run it with output redirected to a file.

For example:

    python meetup_data.py ACCESS_TOKEN members PyData-Edinburgh > PyData-Edinburgh-members.csv

Works with Python 2.7, 3.6 and 3.7.

Installation
------------

There isn't any installational mechanism provided. It's just a python
script that you run directly. It has a single dependency, the `requests`
module, which you need to have installed:

    python -m pip install requests


License
-------

This is licensed as free to use by anyone, without warrantee.


Options
-------

  - **-h**: Show detailed help.

  - **--json**: Save results as raw nested JSON. By default the data is
                written as a CSV file to make it more suitable to use as an
                analytical dataframe (or just to load into Excel).

  - **--identifiable**: Include identifiable data (i.e. people's full names).
                        By default, names are removed.

  - **--firstname**: Include people's first names, but remove any surnames.


Entities
--------

  - **members**: Get information about members of a group. You need to
    provide the group name (from its URL, e.g. PyData-Edinburgh).

  - **future-events**: Get information about upcoming and in-progress
    events for a group (for those groups that support it).

  - **past-events**: Get information about ended (not upcoming or in-progress)
    events for a group (for those groups that support it).

  - **attendance**: Get information about attendance of an individual event
    for a group. You need to provide the group name and also its event_id.
    You can only get attendance data for events that have already happened.

  - **activity**: Get information about activity on all of the groups that
    you are a member of. You don't give it any parameters.


Access Token
------------

To get an access token, the easiest way is to go to the site:
        https://meetuptoken.herokuapp.com
in your browser, then grant it access to your meetup.com account when it asks
you to. It will display your access token.

This app uses the Meetup OAuth2 Implicit Flow to authorize against
your own meetup.com account to allocate, directly, an access token.

However, you might not want to do that (if you don\'t trust what that app
is doing to fetch a token).

So the alternative is to run the same Implicit Flow manually yourself:

   1. Login to https://www.meetup.com/meetup_api/, and create your own
      OAuth Consumer, with redirect_uri as https://www.google.com.
   2. Go to the site:
        https://secure.meetup.com/oauth2/authorize?client_id=CONSUMER_KEY&response_type=token&redirect_uri=https://www.google.com
      in your browser (replacing CONSUMER_KEY with your own consumer key).
   3. Grant it access to your meetup.com account.
   4. It will redirect you to https://www.google.com, with an access token
      embedded within the URL. It's not using google.com for anything, it's
      just needs a site to redirect to.
   5. Look at the new URL in the search bar, and grab the access_token
      property.

An access token will usually expire after an hour.


Heroku App
----------

The sources for the heroku app (deployed at meetupdata.herokuapp.com) are
included as part of this repository. They contain hardwired details for an
OAuth Consumer with a redirect pointing at https://meetuptoken.herokuapp.com,
so, unless modified,  can only be used for that site.

