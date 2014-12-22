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
###Get popular movies in one page:
```
from yify import popular

movies = popular()
print(movies[0]['title'])
```

###Get popular movies in multiple pages:
```
from yify import popular

# get popular movies from page 1 to 21
movies = popular(1, 21)
print(movies[0]['title'])
```

###Get latest movies:
```
from yify import latest

movies = latest()
print(movies[0]['title'])
```

###Search movies:
```
from yify import search

movies = search('django')
print(movies[0]['title'])
```
