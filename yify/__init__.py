import asyncio

import aiohttp
from lxml import etree

base_url = 'http://www.yify-torrent.org'

NUM_COROUTINES = 30


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
            root.xpath('//div[@class="cover"]/img')[0].attrib['src']

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
        imgs = root.xpath('//div[@class="scrshot"]//img')
        movie['screenshot'] = [i.attrib['src'] for i in imgs]

        # get plot
        movie['plot'] = root.xpath('//div[@class="info"]/p')[0].text

    return movie


@asyncio.coroutine
def get_movies(kind, page, search, future, sem):
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

            # find movie poster image
            poster =\
                mv.xpath('.//div[@class="movie-image"]//img')[0].attrib['src']

            # put movie data into dictionary
            movie = {
                'title': title,
                'link': link,
                'poster_small': poster,
            }

            # find movie informations like genre, qualit, etc
            for li in mv.xpath('.//li'):
                # strip space for each text segments
                texts = list(text.strip() for text in li.itertext())

                # use first segment as key
                # lowercase, remove : and replace space with underscore
                key = texts[0].lower().replace(':', '').replace(' ', '_')

                # others as value, and join all as one string
                value = ' '.join(texts[1:]).strip()
                movie[key] = value

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


def latest(from_page=1, to_page=1):
    '''Show latest movies.'''
    # create a semaphore to limit coroutine numbers
    sem = asyncio.Semaphore(NUM_COROUTINES)

    # create an event loop
    loop = asyncio.get_event_loop()

    futures = []
    # create a new future for each page
    for page in range(from_page, to_page + 1):
        # use future to wrap a an asynchronous execution
        future = asyncio.Future()
        asyncio.async(get_movies('latest', page, None, future, sem))
        futures.append(future)

    # wait for all futures to complete
    loop.run_until_complete(asyncio.wait(futures))

    results = []
    # iterate through each future, then get results and append to results
    for f in futures:
        results += f.result()
    return results


def popular(from_page=1, to_page=1):
    '''Show popular movies.'''
    # create a semaphore to limit coroutine numbers
    sem = asyncio.Semaphore(NUM_COROUTINES)

    # create an event loop
    loop = asyncio.get_event_loop()

    futures = []
    # create a new future for each page
    for page in range(from_page, to_page + 1):
        # use future to wrap a an asynchronous execution
        future = asyncio.Future()
        asyncio.async(get_movies('popular', page, None, future, sem))
        futures.append(future)

    # wait for all futures to complete
    loop.run_until_complete(asyncio.wait(futures))

    results = []
    # iterate through each future, then get results and append to results
    for f in futures:
        results += f.result()
    return results


def search(keyword, from_page=1, to_page=1):
    '''Search movies.'''
    # replace space with %20
    keyword = keyword.replace(' ', '%20')

    # create a semaphore to limit coroutine numbers
    sem = asyncio.Semaphore(NUM_COROUTINES)

    # create an event loop
    loop = asyncio.get_event_loop()

    futures = []
    # create a new future for each page
    for page in range(from_page, to_page + 1):
        # use future to wrap a an asynchronous execution
        future = asyncio.Future()
        asyncio.async(get_movies('search', page, keyword, future, sem))
        futures.append(future)

    # wait for all futures to complete
    loop.run_until_complete(asyncio.wait(futures))

    results = []
    # iterate through each future, then get results and append to results
    for f in futures:
        results += f.result()
    return results


def main():
    movies = latest(1, 3)
    for m in movies:
        print('{}: {}'.format(m['title'], m['rating']))

if __name__ == '__main__':
    main()
