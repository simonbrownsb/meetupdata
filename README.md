# meetupdata

Summary
-------

This utility fetches data from the meetup.com API.

It can be used to fetch information about the following entities:\n'
  - members
  - activity
  - events
  - attendance

It writes output to standard output, in JSON format. You should run it with
output redirected to a file.

For example:

    python meetup_data.py ACCESS_TOKEN members PyData-Edinburgh > PyData-Edinburgh-members.json


This is licensed as free to use by anyone, without warrantee.


Installation
------------

There isn't any installational mechanism provided. It's just a python
script that you run directly. It has a single dependency, the `requests`
module, which you need to have installed:

    python -m pip install requests


Entities
--------

  - **members**: Get information about members of a group. You need to
    provide the group name (from its URL, e.g. PyData-Edinburgh).

  - **events**: Get information about events for a group.

  - **attendance**: Get information about attendance of an individual event
    for a group. You need to provide the group name and also its event_id.

  - **activity**: Get information about your own activity. You don't
    provide any group names; it uses all of the groups that you are
    a member of.


Access Token
------------

To get an access token, the easiest way is to go to the site:
        https://meetuptoken.herokuapp.com
in your browser, then grant it access to your meetup.com account when it asks
you to. It will display your access token.

However, you might not want to do that (if you don\'t trust what that app
is doing to fetch a token).

So the alternative is to do it manually yourself:

   1. Login to https://www.meetup.com/meetup_api/, and create your own
      OAuth Consumer, with redirect_uri as https://www.google.com.
   2. Go to the site:
        https://secure.meetup.com/oauth2/authorize?client_id=CONSUMER_KEY&response_type=token&redirect_uri=https://www.google.com
      in your browser (replacing CONSUMER_KEY with your own consumer key.
   3. Grant it access to your meetup.com account.
   4. It will redirect you to https://www.google.com, with an access token
      embedded within the URL. It's not using google.com for anything, it's
      just needs a site to redirect to.
   5. Look at the new URL in the search bar, and grab the access_token
      property.

An access token will usually expire after an hour.

