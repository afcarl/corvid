"""

Fetcher grabs JSON papers from some Server and returns it as a Paper object

"""

from typing import Dict, List

import sys
import re
import warnings

from python.util import parse_arguments
from python.server import Server, ElasticSearchServer


class Mention(object):
    def __init__(self, as_str: str):
        self.as_str = as_str
        try:
            self.as_num = int(as_str)
        except:
            self.as_num = float(as_str)
        self.as_span = None

    def __repr__(self):
        return self.as_str


# TODO: this regex catches 10,000,000 as 3 separate matches
class Paper(object):
    def __init__(self, paper: Dict):
        self._paper = paper
        self.mentions = self.find_mentions()

    @property
    def id(self):
        return self._paper.get('id')

    @property
    def abstract(self):
        return self._paper.get('paperAbstract')

    @property
    def venue(self):
        return self._paper.get('venue')

    def find_mentions(self) -> List[Mention]:
        mentions = re.findall(pattern=r'[-+]?\d*\.\d+|\d+',
                              string=self.abstract)
        mentions = [Mention(as_str=m) for m in mentions]

        is_duplicates = len(mentions) != len(set([m.as_num for m in mentions]))
        if is_duplicates:
            warnings.warn('Duplicate mentions in paper_id {}'.format(self.id))

        return mentions


# TODO: Only supporting 100 papers at once, just to keep ES server happy
class Fetcher(object):
    MAX_BATCH_SIZE = 100
    def __init__(self, server: Server):
        self.server = server

    def __call__(self, paper_ids: List[str]) -> List[Paper]:
        if len(paper_ids) > Fetcher.MAX_BATCH_SIZE:
            raise Exception('Too many papers at once!')
        papers = []
        for paper_id in paper_ids:
            print('Fetching paper_id {}'.format(paper_id))
            try:
                papers.append(Paper(self.server.get_paper_by_id(paper_id)))
            except Exception:
                print('Skipping paper_id {}'.format(paper_id))

        return papers


if __name__ == '__main__':
    args = parse_arguments(sys.argv[1:])
    es_server = ElasticSearchServer(url=args.url, port=args.port)
    fetcher = Fetcher(server=es_server)
    papers = fetcher(paper_ids=[args.paper_id])
