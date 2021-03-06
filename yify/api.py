import asyncio

import aiohttp
from lxml import etree

base_url = 'http://www.yify-torrent.org'


@asyncio.coroutine
def get_one(url, sem):
    with (yield from sem):
        '''Get informations of the specific movie.'''
        # get page content by asyncio
        res = yield from aiohttp.request('GET', url)
        content = yield from res.text()

        movie = {}

        # use lxml to find the informations we want
        root = etree.HTML(content)

        # get movie poster
        movie['poster_large'] =\
            'https:' + root.xpath('//div[@class="cover"]/img')[0].attrib['src']

        # get movie details
        for li in root.xpath('//div[@class="inattr"]//li'):
            # strip space for each text segments
            texts = list(text.strip() for text in li.itertext())

            # use first segment as key
            # lowercase, remove : and replace space with underscore
            key = texts[0].lower().replace(':', '').replace(' ', '_')

            # others as value, and join all as one string
            value = ' '.join(texts[1:]).strip()
            movie[key] = value

            # get imdb link if key is imdb_rating
            if key == 'imdb_rating':
                movie['imdb'] = li.xpath('./a')[0].attrib['href']

        attrs = root.xpath('//div[@class="outattr"]/div[@class="attr"]')
        # get trailer
        movie['trailer'] = attrs[1].xpath('./a')[0].attrib['href']
        # get magnet
        movie['magnet'] = attrs[2].xpath('./a')[0].attrib['href']

        # get screenshots
        imgs = root.xpath('//div[contains(@class,"scrshot")]//img')
        movie['screenshot'] = ['https:' + i.attrib['src'] for i in imgs]

        # get plot
        movie['plot'] = root.xpath('//div[@class="info"]/p')[0].text

    return movie


@asyncio.coroutine
def get_all(kind, page, search, future, sem):
    with (yield from sem):
        '''Get all movies by specifing kind.'''
        # use semaphore to limit the number of coroutines
        url = get_url(kind, page, search)
        # check url is None
        if url is None:
            return future.set_result([])

        # get page content by asyncio
        res = yield from aiohttp.request('GET', url)
        content = yield from res.text()

        movies = []

        # use lxml to find the informations we want
        root = etree.HTML(content)
        # every movie is inside a div with class mv
        for mv in root.xpath('//div[@class="mv"]'):
            a = mv.xpath('./h3')[0].xpath('./a')[0]
            # get movie title
            title = a.text
            # get yify link
            link = base_url + a.attrib['href']

            # put movie data into dictionary
            movie = {
                'title': title,
                'link': link,
            }

            # append movie into movies
            movies.append(movie)

    # get informations from the movie's yify link
    for movie in movies:
        detail = yield from get_one(movie['link'], sem)
        movie.update(detail)

    future.set_result(movies)


def get_url(kind, page, search=None):
    '''Use kind to generate different url.'''
    kind = kind.lower()
    if kind == 'search' and search is not None:
        return '{}/search/{}/t-{}/'.format(base_url, search, page)
    elif kind in ['latest', 'popular']:
        return '{}/{}-{}.html'.format(base_url, kind, page)
