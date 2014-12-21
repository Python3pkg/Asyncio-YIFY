Asyncio-YIFY
============

Damned fast YIFY parser using Asyncio
---------------------------------------------------

YIFY official API doesn't provide method to get popular movies, so I write one.

I use Asyncio powerd by Python 3.4, so it's pretty fast.

Installation
-------------
`pip install asyncio-yify`

or

`python setup.py install`

Usage
------
###Import asyncio and yify package, then get event loop:
```
import asyncio
import yify

loop = asyncio.get_event_loop()
```

###Get popular movies in one page:
```
@asyncio.coroutine
def foo():
    movies = yield from yify.popular(1)

    # print first movie title
    print(movies[0]['title'])

loop.run_until_complete(foo())
```

###Get popular movies in multiple pages:
```
# get popular movies from page 1 to 21
@asyncio.coroutine
def foo():
    # create a list of coroutines from page 1 to 10
    tasks = [yify.popular(i) for i in range(1, 11)]
    
    for f in asyncio.as_completed(tasks):
        movies = yield from f
        
        # print each movie rating and title
        for movie in movies:
            print(movie['rating'], movie['title'])

loop.run_until_complete(foo())
```

###Get latest movies:
```
@asyncio.coroutine
def foo():
    movies = yield from yify.latest(1)

    # print first movie title
    print(movies[0]['title'])

loop.run_until_complete(foo())
```

###Search movies:
```
@asyncio.coroutine
def foo():
    movies = yield from yify.search('django', 1)

    # print first movie title
    print(movies[0]['title'])

loop.run_until_complete(foo())
```
