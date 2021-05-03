from random import choice

from urllib.request import Request

USER_AGENTS = (
    # Chrome Windows
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
    # Firefox Windows
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) '
    'Gecko/20100101 Firefox/46.0',
    # IE Windows
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
)


class ScrapeRequest(Request):

    def __init__(self, url, *args, **kwargs):
        super(ScrapeRequest, self).__init__(url, *args, **kwargs)

    def random_user_agent(self):
        return choice(USER_AGENTS)


class TrackInfoRequest(ScrapeRequest):

    ROOT_URL = 'http://www.trackinfo.com/trackdocs/hound/'

    def __init__(self, url, *args, **kwargs):
        super(TrackInfoRequest, self).__init__(url, *args, **kwargs)
        self.url = url
        self.add_header(
                'User-Agent',
                self.random_user_agent())
        self.origin_req_host = '%s?breed=g' % self.ROOT_URL
