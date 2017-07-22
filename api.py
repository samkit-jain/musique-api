import sqlite3
import re
from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource

DB_NAME = 'musique.db'
RATING_PATTERN = re.compile(r'^([1-9]\.[0-9])|(0\.[1-9])$')

app = Flask(__name__)
api = Api(app)

conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

# Create table for genres
c.execute('''CREATE TABLE IF NOT EXISTS genres(id INTEGER PRIMARY KEY NOT NULL, name TEXT NOT NULL)''')
# Save (commit) the changes
conn.commit()

"""
t1 = [('pop', ), ('rock', ), ('metal', ), ]
c.executemany('INSERT INTO genres VALUES(NULL, ?)', t1)
conn.commit()
"""

# Create table for tracks
c.execute('''CREATE TABLE IF NOT EXISTS tracks(id INTEGER PRIMARY KEY NOT NULL, title TEXT NOT NULL, rating TEXT NOT NULL)''')
conn.commit()

"""
c.execute('INSERT INTO tracks VALUES(NULL, \'T1\', \'4.5\')')
conn.commit()
c.execute('INSERT INTO tracks VALUES(NULL, \'T2\', \'9.5\')')
conn.commit()
c.execute('INSERT INTO tracks VALUES(NULL, \'T3\', \'2.0\')')
conn.commit()
"""

# Create table for saving multiple genres related to a specific track
c.execute('''CREATE TABLE IF NOT EXISTS tracksgenres(track_id INTEGER NOT NULL, genre_id INTEGER NOT NULL, PRIMARY KEY(track_id, genre_id))''')
conn.commit()

"""
c.execute('INSERT INTO tracksgenres VALUES(1, 6)')
conn.commit()
c.execute('INSERT INTO tracksgenres VALUES(1, 11)')
conn.commit()
c.execute('INSERT INTO tracksgenres VALUES(3, 8)')
conn.commit()
c.execute('INSERT INTO tracksgenres VALUES(3, 1)')
conn.commit()
c.execute('INSERT INTO tracksgenres VALUES(1, 3)')
conn.commit()
c.execute('INSERT INTO tracksgenres VALUES(2, 1)')
conn.commit()
"""

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()

# required=False because I'm manually handling the existence
# URL argument parser for genre related operations
parser_genre = reqparse.RequestParser()
parser_genre.add_argument('id', required=False)
parser_genre.add_argument('name', required=False)

# URL argument parser for track related operations
parser_track = reqparse.RequestParser()
parser_track.add_argument('id', required=False)
parser_track.add_argument('title', required=False)
parser_track.add_argument('rating', required=False)
parser_track.add_argument('genres', type=int, action='append', required=False)


# Class for displaying specific genre and edit a genre
class Genre(Resource):

	# Retrieve singe genre
	def get(self, genre_id):
		global DB_NAME

		try:
			conn = sqlite3.connect(DB_NAME)
			c = conn.cursor()
			t = (str(genre_id),)
		
			# Getting single genre
			c.execute('SELECT * FROM genres WHERE id=?', t)

			ret = c.fetchone()
			conn.close()

			if(ret == None): # If no genre related to id
				return {'message': 'not found'}
			else: # Genre found
				return {'id': ret[0] , 'name': ret[1]}
		except:
			return {'message': 'some error occurred'}
	
	# Edit a genre
	def post(self, genre_id):
		global DB_NAME

		try:
			args = parser_genre.parse_args()

			if 'id' in args and 'name' in args and not args['id'] == None and not args['name'] == None: # If both parameters are present in the POST request
				if str(genre_id) == str(args['id']): # If the id in POST and URL match
					conn = sqlite3.connect(DB_NAME)
					c = conn.cursor()
					t = (str(genre_id), )
					c.execute('SELECT * FROM genres WHERE id=?', t)
					ret = c.fetchone()
					conn.close()

					if ret == None or len(ret) == 0: # If genre not present
						return {'message': 'not found'}
					
					# If genre present
					conn = sqlite3.connect(DB_NAME)
					c = conn.cursor()

					stripped = str(args['name']).strip()
					
					if not stripped == "": # If name is not empty
						t = (stripped, str(genre_id), )

						# Edit genre information
						c.execute('UPDATE genres SET name=? WHERE id=?', t)
						conn.commit()
						suc = c.rowcount
						conn.close()

						if suc == 1: # Update successful
							return {'id': str(args['id']), 'name': stripped}
						
						# Update failed
						return {'message': 'edit failed'}
		
					# If name is empty
					conn.close()
					return {'message': 'empty name'}
			
				# If the id in POST and URL do not match
				return {'message': 'id mismatch'}
		
			# If a parameter is missing in the POST request
			return {'message': 'id or name missing'}
		except:
			return {'message': 'some error occurred'}


# Class for displaying all genres and add a genre
class GenreList(Resource):
	
	# Retrieve all genres
	def get(self):
		global DB_NAME

		try:
			conn = sqlite3.connect(DB_NAME)
			c = conn.cursor()

			c.execute('SELECT * FROM genres')

			ret = c.fetchall()
			conn.close()

			if(ret == None): # Empty
				return {'message': 'not found'}
			else: # Not empty
				res = {
					'count': len(ret),
					'results': []
				}

				# Append each genre to list
				for r in ret:
					res['results'].append({'id': r[0] , 'name': r[1]})

				return res
		except:
			return {'message': 'some error occurred'}

	# Add a genre
	def post(self):
		global DB_NAME

		try:
			args = parser_genre.parse_args()

			if 'name' in args and not args['name'] == None: # If name in POST argument
				conn = sqlite3.connect(DB_NAME)
				c = conn.cursor()

				stripped = str(args['name']).strip()
				
				if not stripped == "": # If name not empty
					t = (stripped, )
					c.execute('INSERT INTO genres VALUES(NULL, ?)', t)
					conn.commit()
					suc = c.rowcount
					idv = c.lastrowid # id of new genre
					conn.close()

					if suc == 1: # If insert successful
						return {'id': idv, 'name': stripped}
					else: # Insert failed
						return {'message': 'add failed'}
				else: # If name empty
					conn.close()
					return {'message': 'empty name'}
			else: # If name not in POST argument
				return {'message': 'name missing'}
		except:
			return {'message': 'some error occurred'}


# Class for displaying specific track and edit a track
class Track(Resource):

	# Retrieve singe track
	def get(self, track_id):
		global DB_NAME

		try:
			conn = sqlite3.connect(DB_NAME)
			c = conn.cursor()
			t = (str(track_id),)

			# Getting single track
			c.execute('SELECT * FROM tracks WHERE id=?', t)

			ret = c.fetchone()
			
			if ret == None or len(ret) == 0: # If no track related to id
				conn.close()
				return {'message': 'not found'}
			else: # Track found
				res = {'id': ret[0] , 'title': ret[1], 'rating': ret[2], 'genres': []}	
				
				# Get all genres related to track
				t1 = (ret[0], )
				c.execute('SELECT genres.id, genres.name FROM tracksgenres INNER JOIN genres ON tracksgenres.genre_id=genres.id WHERE tracksgenres.track_id=?', t1)

				ret1 = c.fetchall()

				for c1 in ret1:
					res['genres'].append({'id': c1[0] , 'name': c1[1]})

				conn.close()

				return res
		except:
			return {'message': 'some error occurred'}

	# Edit a track
	def post(self, track_id):
		global DB_NAME

		try:
			args = parser_track.parse_args()

			if 'id' in args and 'title' in args and 'rating' in args and 'genres' in args and not args['id'] == None and not args['title'] == None and not args['rating'] == None and not args['genres'] == None: # If all parameters are present in POST argument
				if str(track_id) == str(args['id']): # If the id in POST and URL match
					conn = sqlite3.connect(DB_NAME)
					c = conn.cursor()

					t3 = (str(track_id), )
					c.execute("SELECT id from tracks WHERE id=?", t3)

					if len(c.fetchall()) == 0:
						return {'message': 'id doesn\'t exist'}

					strippedT = str(args['title']).strip()
					
					if not strippedT == "": # If title not empty
						strippedR = str(args['rating']).strip()

						if not strippedR == "" and re.fullmatch(RATING_PATTERN, strippedR): # If rating matches pattern
							if not len(args['genres']) == 0: #If genres list not empty
								# Removing duplicates
								list1 = list(set(args['genres']))
								
								c.execute('SELECT id from genres')
								allGenres = c.fetchall()

								# REMOVE GENRE IDS NOT PRESENT
								list2 = [x[0] for x in allGenres]
								list1 = list(set(list1).intersection(list2))

								if len(list1) == 0:
									return {'message': 'genre ids are invalid'}
								
								t = (str(track_id), )
								c.execute("DELETE FROM tracksgenres WHERE track_id=?", t)
								conn.commit()

								t = (strippedT, strippedR, track_id)
								c.execute('UPDATE tracks SET title=?, rating=? WHERE id=?', t)
								conn.commit()

								t1 = []

								for item in list1:
									t1.append((track_id, item, ))
								
								c.executemany('INSERT INTO tracksgenres VALUES(?, ?)', t1)
								conn.commit()

								res = {'id': track_id , 'title': strippedT, 'rating': strippedR, 'genres': []}

								t2 = (track_id, )
								c.execute('SELECT genres.id, genres.name FROM tracksgenres INNER JOIN genres ON tracksgenres.genre_id=genres.id WHERE tracksgenres.track_id=?', t2)

								ret1 = c.fetchall()

								for c1 in ret1:
									res['genres'].append({'id': c1[0] , 'name': c1[1]})

								return res
							else: # If genres list empty
								return {'message': 'genres empty'}
						else: # If rating not matches pattern
							conn.close()
							return {'message': 'rating must be in [0.1, 9.9]'}
					else: # If title empty
						conn.close()
						return {'message': 'empty title'}
				else: # If the id in POST and URL do not match
					return {'message': 'id mismatch'}
			else: # If a parameter is missing in the POST request
				return {'message': 'id, title, rating or genres missing'}
		except:
			return {'message': 'some error occurred'}

# Class for displaying all tracks and add a track
class TrackList(Resource):
	
	# Retrieve all tracks
	def get(self):
		global DB_NAME

		try:
			args = parser_track.parse_args()

			if 'title' in args and not args['title'] == None:
				conn = sqlite3.connect(DB_NAME)
				c = conn.cursor()

				t = ('%' + str(args['title']) + '%', )
				c.execute('SELECT * FROM tracks WHERE title LIKE ?', t)

				ret = c.fetchall()

				if(ret == None): # Empty
					conn.close()
					return {'message': 'not found'}
				else: # Not empty
					res = {
						'count': len(ret),
						'results': []
					}

					# Append each genre to list
					for r in ret:
						res['results'].append({'id': r[0] , 'title': r[1], 'rating': r[2], 'genres': []})

						t = (r[0], )
						c.execute('SELECT genres.id, genres.name FROM tracksgenres INNER JOIN genres ON tracksgenres.genre_id=genres.id WHERE tracksgenres.track_id=?', t)

						ret1 = c.fetchall()

						l = len(res['results']) - 1

						for c1 in ret1:
							res['results'][l]['genres'].append({'id': c1[0] , 'name': c1[1]})

					conn.close()

					return res
			else:
				conn = sqlite3.connect(DB_NAME)
				c = conn.cursor()

				c.execute('SELECT * FROM tracks')

				ret = c.fetchall()

				if(ret == None): # Empty
					conn.close()
					return {'message': 'not found'}
				else: # Not empty
					res = {
						'count': len(ret),
						'results': []
					}

					# Append each genre to list
					for r in ret:
						res['results'].append({'id': r[0] , 'title': r[1], 'rating': r[2], 'genres': []})

						t = (r[0], )
						c.execute('SELECT genres.id, genres.name FROM tracksgenres INNER JOIN genres ON tracksgenres.genre_id=genres.id WHERE tracksgenres.track_id=?', t)

						ret1 = c.fetchall()

						l = len(res['results']) - 1

						for c1 in ret1:
							res['results'][l]['genres'].append({'id': c1[0] , 'name': c1[1]})

					conn.close()

					return res
		except:
			return {'message': 'some error occurred'}

	# Add a track
	def post(self):
		global DB_NAME

		try:
			args = parser_track.parse_args()

			if 'title' in args and 'rating' in args and 'genres' in args and not args['title'] == None and not args['rating'] == None and not args['genres'] == None: # If title, rating and genres are present in POST argument
				conn = sqlite3.connect(DB_NAME)
				c = conn.cursor()

				strippedT = str(args['title']).strip()
				
				if not strippedT == "": # If title not empty
					strippedR = str(args['rating']).strip()

					if not strippedR == "" and re.fullmatch(RATING_PATTERN, strippedR): # If rating matches pattern
						if not len(args['genres']) == 0: #If genres list not empty
							# Removing duplicates
							list1 = list(set(args['genres']))
							
							c.execute('SELECT id from genres')
							allGenres = c.fetchall()

							# REMOVE GENRE IDS NOT PRESENT
							list2 = [x[0] for x in allGenres]
							list1 = list(set(list1).intersection(list2))

							if len(list1) == 0:
								return {'message': 'genre ids are invalid'}
								
							t = (strippedT, strippedR, )
							c.execute('INSERT INTO tracks VALUES(NULL, ?, ?)', t)
							conn.commit()
							idv = c.lastrowid # id of new track

							t1 = []

							for item in list1:
								t1.append((idv, item, ))
							
							c.executemany('INSERT INTO tracksgenres VALUES(?, ?)', t1)
							conn.commit()

							res = {'id': idv , 'title': strippedT, 'rating': strippedR, 'genres': []}

							t2 = (idv, )
							c.execute('SELECT genres.id, genres.name FROM tracksgenres INNER JOIN genres ON tracksgenres.genre_id=genres.id WHERE tracksgenres.track_id=?', t2)

							ret1 = c.fetchall()

							for c1 in ret1:
								res['genres'].append({'id': c1[0] , 'name': c1[1]})

							return res
						else: # If genres list empty
							return {'message': 'genres empty'}
					else: # If rating not matches pattern
						conn.close()
						return {'message': 'rating must be in [0.1, 9.9]'}
				else: # If title empty
					conn.close()
					return {'message': 'empty title'}
			else: # If title, rating or genres not in POST argument
				return {'message': 'title, rating or genres missing'}
		except:
			return {'message': 'some error occurred'}


# Setup the API resource routing here
api.add_resource(GenreList, '/v1/genres')
api.add_resource(Genre, '/v1/genres/<int:genre_id>')
api.add_resource(TrackList, '/v1/tracks')
api.add_resource(Track, '/v1/tracks/<int:track_id>')


if __name__ == '__main__':
	app.run(debug=True)