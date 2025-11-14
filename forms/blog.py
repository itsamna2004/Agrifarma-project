from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class PostForm(FlaskForm):
    title = StringField('Post Title', validators=[
        DataRequired('Title is required'),
        Length(min=5, max=255, message='Title must be between 5 and 255 characters')
    ])
    content = TextAreaField('Content', validators=[
        DataRequired('Content is required'),
        Length(min=10, message='Content must be at least 10 characters')
    ])
    post_image = FileField('Post Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')])
    submit = SubmitField('Post')


class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[
        DataRequired('Comment cannot be empty'),
        Length(min=1, max=500, message='Comment must be between 1 and 500 characters')
    ])
    submit = SubmitField('Post Comment')

