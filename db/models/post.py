from sqlalchemy.orm import validates
from ..shared import db
from db.models.user import User


class Post(db.Model):
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    likes = db.Column(db.Integer, default=0, nullable=False)
    reads = db.Column(db.Integer, default=0, nullable=False)
    popularity = db.Column(db.Float, default=0.0, nullable=False)
    users = db.relationship("User", secondary="user_post", viewonly=True)

    # note: comma separated string since sqlite does not support arrays
    _tags = db.Column("tags", db.String, nullable=False)

    # getter and setter for tags column.
    # converts list to string when value is set and string to list when value is retrieved.
    @property
    def tags(self):
        return self._tags.split(",")

    @tags.setter
    def tags(self, tags):
        self._tags = ",".join(tags)

    @validates("popularity")
    def validate_popularity(self, key, popularity) -> str:
        if popularity > 1.0 or popularity < 0.0:
            raise ValueError("Popularity should be between 0 and 1")
        return popularity

    def serialize(self, withUsers=False):
        # adapted from
        # https://stackoverflow.com/questions/7102754/jsonify-a-sqlalchemy-result-set-in-flask
        """returns object in easily serialized (jsonify-able) format"""
        serialized = {
            "id": self.id,
            "text": self.text,
            "likes": self.likes,
            "reads": self.reads,
            "popularity": self.popularity,
            "tags": self.tags,
        }

        if withUsers:
            user_ids = []
            for user in self.users:
                user_ids.append(user.id)
            serialized["authorIds"] = sorted(user_ids)

        return serialized

    @property
    def serialize_with_users(self):
        """returns object in easily serialized (jsonify-able format)"""

    def __str__(self):
        self_str = (
            "-----Post-----\n"
            + f"ID: {self.id}\n"
            + f"Text: {self.text}\n"
            + f"Likes: {self.likes}\n"
            + f"Reads: {self.reads}\n"
            + f"Popularity: {self.popularity}\n"
            + f"Tags: {self.tags}\n"
            + f"Users: {self.users}\n"
            "--------------"
        )
        return self_str

    @staticmethod
    def get_posts_by_user_id(user_id):
        user = User.query.get(user_id)
        return Post.query.with_parent(user).all()

    @staticmethod
    def get_post_by_post_id(post_id):
        return Post.query.get(post_id)
