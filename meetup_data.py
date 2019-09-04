# -*- coding: utf-8 -*-

#
# Little script for fetching data from meetup.com through it's API.
#

from __future__ import print_function

import argparse
import json
import sys
from collections import OrderedDict

import requests

OAUTH_URL = 'https://secure.meetup.com/oauth2/authorize'
MEETUP_URL = 'https://api.meetup.com'


class MeetupAPI:
    """
    Class for accessing Meetup API using an OAuth2 access token.

    It requires you to have already fetched the access token; it doesn't
    allocate one automatically.

    The simplest way to get an access token is to browse to:
        https://meetuptoken.herokuapp.com

    """
    def __init__(self, access_token,
                 anon_level=1, debug_level=1, stop_after_one=False):
        self.access_token = access_token
        self.anon_level = anon_level
        self.debug_level = debug_level
        self.stop_after_one = stop_after_one

    def get_json(self, method, params, pi_fields, order):
        headers = {'Authorization': 'Bearer %s' % self.access_token}
        allparams = {
            'format': 'json',
            'page': 100,
            'order': order,
        }
        allparams.update(params)
        items = []
        next_url = None
        while True:
            if next_url:
                if self.debug_level > 0:
                    print(next_url, file=sys.stderr)
                r = requests.get(next_url, headers=headers)
            else:
                if self.debug_level > 0:
                    print(MEETUP_URL + method
                          + '?' + '&'.join(['%s=%s' % (k, v)
                                           for k, v in allparams.items()]),
                          file=sys.stderr)
                r = requests.get(MEETUP_URL + method, params=allparams,
                                 headers=headers)

            if self.debug_level > 0:
                print('... %s' % r.status_code, file=sys.stderr)
            if r.status_code == 200:
                try:
                    doc = json.loads(r.text)
                except ValueError as e:
                    print(str(e), file=sys.stderr)
                    print(r.text, file=sys.stderr)
                    sys.exit(1)
                except Exception as e:
                    print('Failure: %s %s' % (e.__class__.__name__, str(e)),
                          file=sys.stderr)
                    sys.exit(1)

                if 'results' in doc:
                    results = doc['results']
                    if self.stop_after_one:
                        results = results[:1]
                else:
                    results = doc
                for item in results:
                    self.anonymise(item, pi_fields, self.anon_level)
                    if self.debug_level > 1:
                        print(item, file=sys.stderr)
                items.extend(results)

                if 'meta' in doc and 'next' in doc['meta']:
                    next_url = doc['meta']['next']
                if self.stop_after_one or not next_url:
                    return items
            else:
                print('Request failed with status %d' % r.status_code,
                      file=sys.stderr)
                try:
                    doc = json.loads(r.text)
                    for k, v in doc.items():
                        print('%s: %s' % (k, v), file=sys.stderr)
                except ValueError as e:
                    print(str(e), file=sys.stderr)
                    print(r.text, file=sys.stderr)
                sys.exit(1)

    @staticmethod
    def anonymise(item, pi_fields, level):
        """
        Anonymise a single record by replacing or truncating values that
        are people's names.
        """
        if type(item) is dict:
            for a in pi_fields:
                if a in item:
                    if level == 2:
                        # completely remove name
                        item[a] = '...'
                    elif level == 1:
                        # just take first word (first name, discard surname)
                        parts = item[a].split()
                        if len(parts) > 1:
                            item[a] = parts[0]
                else:
                    # recurse
                    for k, v in item.items():
                        self.anonymise(v, pi_fields, level)

    def get_members(self, params):
        """
        get info about all members of a specified group
        """
        pi_fields = ['name']
        if not params:
            print('members requires a group name (from its URL)',
                  file=sys.stderr)
            sys.exit(1)
        params = {'group_urlname': params[0]}
        return self.get_json('/2/members', params, pi_fields, 'joined')

    def get_activity(self, params):
        """
        get all activity for all groups you are a member of
        """
        pi_fields = ['member_name']
        if params:
            print('activity does not take any parameter', file=sys.stderr)
            sys.exit(1)
        return self.get_json('/activity', {}, pi_fields, 'updated')

    def get_events(self, params):
        """
        get info about all events for a specified group
        """
        pi_fields = []
        if not params:
            print('events requires a group name (from its URL)',
                  file=sys.stderr)
            sys.exit(1)
        endpoint = '/%s/events' % params[0]
        return self.get_json(endpoint, {}, pi_fields, 'updated')

    def get_attendance(self, params):
        """
        get info about attendance for a specified event
        """
        pi_fields = ['name']
        if len(params) != 2:
            print('attendance requires a group name and an event id',
                  file=sys.stderr)
            sys.exit(1)
        endpoint ='/%s/events/%s/attendance' % (params[0], params[1])
        return self.get_json(endpoint, {}, pi_fields, 'time')

    @staticmethod
    def flatten(row, expand):
        """
        Convert from arbitrarily-nested data structure to a flattened
        form, more suitable for using as an analytical dataframe.
        """
        result = OrderedDict()
        for k, v in row.items():
            if type(v) is dict:
                for k2, v2 in v.items():
                    result[k + '_' + k2] = v2
            elif expand and type(v) in (list, tuple):
                for i, item in enumerate(v):
                    if type(item) is dict:
                        for (k2, v2) in item.items():
                            result[k + '_' + str(i) + '_' + k2] = v2
                    else:
                        result[k + '_' + str(i)] = item
            else:
                result[k] = v
        return result


def main(argv):
    description = (
        '\n'
        '----------------------------------------------------------------\n'
        'This utility fetches data from the meetup.com API.\n'
        'It can be used to fetch information about the following entities:\n'
        '   - members\n'
        '   - activity\n'
        '   - events\n'
        '   - attendance\n\n'
        'It writes output to standard output, in JSON format. You should\n'
        'run it with output redirected to a file.\n\n'
        'For example:\n'
        '    python meetup_data.py ACCESS_TOKEN members PyData-Edinburgh > PyData-Edinburgh-members.json\n'
        '----------------------------------------------------------------\n'
    )
    epilog = (
        '----------------------------------------------------------------\n'
        'To get an access token, the easiest way is to go to the site:\n'
        '        https://meetuptoken.herokuapp.com\n'
        'in your browser, then grant it access to your meetup.com account\n'
        'when it asks you to. It will display your access token.\n\n'
        'However, you might not want to do that (if you don\'t trust what that\n'
        'app is doing to fetch a token). So the alternative is to do it\n'
        'manually yourself:\n\n'
        '   1. Login to https://www.meetup.com/meetup_api/, and create your\n'
        '      own OAuth Consumer, with redirect_uri as https://www.google.com\n'
        '   2. Go to the site:\n'
        '        %s?client_id=CONSUMER_KEY&response_type=token&redirect_uri=https://www.google.com\n'
        '      in your browser (replacing CONSUMER_KEY with your own consumer key)\n'
        '   3. Grant it access to your meetup.com account\n'
        '   4. It will redirect you to https://www.google.com, with an access\n'
        '      token embedded within the URL. It\'s not using google.com for\n'
        '      anything, it\'s just needs a site to redirect to.\n'
        '   5. Look at the new URL in the search bar, and grab the access_token property.\n\n'
        'An access token will usually expire after an hour.\n'
        '----------------------------------------------------------------\n'
        % OAUTH_URL
    )

    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(prog='meetup_data',
                                     description=description,
                                     epilog=epilog,
                                     formatter_class=formatter)
                                      
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Run quietly, without displaying the URLs used')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print out each data chunk as it is read')
    parser.add_argument('--raw', action='store_true',
                        help='Write out results in raw nested JSON form '
                             '(without any flattening, so not suitable for '
                             'using directly as an analytical dataframe)')
    parser.add_argument('--identifiable', action='store_true',
                        help='Retain identifiable information about people')
    parser.add_argument('--firstname', action='store_true',
                        help='Retain people\'s first names but not surnames')
    parser.add_argument('--stop_after_one', action='store_true',
                        help='Stop after reading a single record '
                             '(for debugging)')
    parser.add_argument('access_token', help='Meetup oauth2 access_token',
                        nargs='?')
    parser.add_argument('entity', nargs='?',
                        help='One of: members, activity, events, attendance')
    parser.add_argument('params', nargs='*',
                        help='Parameter to filter by:\n'
                             '   for members:    the group name\n'
                             '   for events:     the group name\n'
                             '   for attendance: the group name and event_id\n'
                             '   for activity:   not used, it just uses the '
                             'groups you are members of\n')
    flags = parser.parse_args(argv)

    if flags.identifiable and flags.firstname:
        print('You cannot use both --identifiable and --firstname together',
              file=sys.stderr)

    if (flags.access_token is None or flags.entity is None
                                   or flags.entity == 'help'):
        print('Run with the -h option to get help on how to run this.',
              file=sys.stderr)
        sys.exit(0)

    anon_level = 0 if flags.identifiable else 1 if flags.firstname else 2
    debug_level = 0 if flags.quiet else 2 if flags.verbose else 0
    client = MeetupAPI(flags.access_token,
                       anon_level=anon_level,
                       debug_level=debug_level,
                       stop_after_one=flags.stop_after_one)

    if flags.entity == 'members':
        result = client.get_members(flags.params)
    elif flags.entity == 'activity':
        result = client.get_activity(flags.params)
    elif flags.entity == 'events':
        result = client.get_events(flags.params)
    elif flags.entity == 'attendance':
        result = client.get_attendance(flags.params)
    else:
        print('Error: unknown entity type %s' % flags.entity,
              file=sys.stderr)
        sys.exit(1)
    if not flags.raw:
        result = [client.flatten(r, True) for r in result]
    print(json.dumps(result))


if __name__ == '__main__':
    main(sys.argv[1:])

