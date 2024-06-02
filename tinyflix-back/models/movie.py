class Movie:
    def __init__(self, id, title, genre, director, actors, rating, s3_path):
        self.id = id
        self.title = title
        self.genre = genre
        self.director = director
        self.actors = actors
        self.rating = rating
        self.s3_path = s3_path


    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'genre': self.genre,
            'director': self.director,
            'actors': self.actors,
            'rating': self.rating,
            's3_key': self.s3_key
        }

