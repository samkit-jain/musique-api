# musique-api

A simple REST API using [flask-resful](https://github.com/flask-restful/flask-restful)

# How To Use

1. Open terminal
1. ```cd path/to/api.py```
1. ```python3 api.py```
1. Open another terminal
1. For POST request: ```curl http://localhost:5000/v1/tracks/23 -d "id=23&title=title23&rating=9.9&genres=12&genres=3" -X POST -v```
1. For GET request: Open http://localhost:5000/v1/tracks in your browser

# Usage

List all genres
HTTP GET to http://localhost:5000/v1/genres
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "name": "rock"
    },
    {
      "id": 2,
      "name": "metal"
    },
    {
      "id": 3,
      "name": "indie"
    }
  ]
}
```

Get single genre record
HTTP GET to http://localhost:5000/v1/genres/1  #here 1 in genres/1 is the ID of the genre
```json
{
  "id": 1,
  "name": "rock"
}
```

Edit genre record
HTTP POST to http://localhost:5000/v1/genres/1
```json
{
  "id": 1,
  "name": "pop"
}
```

Create new genre
HTTP POST to http://localhost:5000/v1/genres
```json
{
  "name": "edm"
}
```

List all tracks
HTTP GET to http://localhost:5000/v1/tracks
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "title": "Numb",
      "rating": "9.5",
      "genres": [
        {
          "id": 1,
          "name": "rock"
        }
      ]
    },
    {
      "id": 2,
      "title": "Hey mama",
      "rating": "5.9",
      "genres": [
        {
          "id": 4,
          "name": "edm"
        },
        {
          "id": 5,
          "name": "house"
        }
      ]
    }
  ]
}
```

Search track
HTTP GET to http://localhost:5000/v1/tracks?title=Hey
```json
{
  "count": 1,
  "results": [
    {
      "id": 2,
      "title": "Hey mama",
      "rating": "5.9",
      "genres": [
        {
          "id": 4,
          "name": "edm"
        },
        {
          "id": 5,
          "name": "house"
        }
      ]
    }
  ]
}
```

Get single track record
HTTP GET to http://localhost:5000/v1/tracks/2
```json
{
  "id": 2,
  "title": "Hey mama",
  "rating": "5.9",
  "genres": [
    {
      "id": 4,
      "name": "edm"
    },
    {
      "id": 5,
      "name": "house"
    }
  ]
}
```

Edit track
HTTP POST to http://localhost:5000/v1/tracks/1
```json
{
  "id": 1,
  "title": "new title",
  "rating": 4.5,
  "genres": [2]
}
```

Add track
HTTP POST to http://localhost:5000/v1/tracks
```json
{
  "title": "new title",
  "rating": 9.5,
  "genres": [1, 4]
}
```
