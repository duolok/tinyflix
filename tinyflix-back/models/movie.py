class Movie:
    def __init__(self, id, title, genre, director, actors, rating, s3_key, file_name, file_type, file_size, creation_time, last_modified_time, description=None):
        self.id = id
        self.title = title
        self.genre = genre
        self.director = director
        self.actors = actors
        self.rating = rating
        self.s3_key = s3_key
        self.file_name = file_name
        self.file_type = file_type
        self.file_size = file_size
        self.creation_time = creation_time
        self.last_modified_time = last_modified_time
        self.description = description

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'genre': self.genre,
            'director': self.director,
            'actors': self.actors,
            'rating': self.rating,
            's3_key': self.s3_key,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'creation_time': self.creation_time,
            'last_modified_time': self.last_modified_time,
            'description': self.description
        }

