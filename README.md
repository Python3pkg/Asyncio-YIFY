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
###Import asyncio and yify package, and get event loop:
```
import asyncio
import yify

loop = asyncio.get_event_loop()
```

###Get popular movies in one page:
```
loop.run_until_complete(yify.popular(1))
```

###Get popular movies in multiple pages:
```
# get popular movies from page 1 to 21
f = asyncio.wait([popular(page) for page in range(1, 21)])
loop.run_until_complete(f)
```

###Get latest movies:
```
loop.run_until_complete(yify.latest(1))
```

###Search movies
```
loop.run_until_complete(yify.search('django', 1))
```
