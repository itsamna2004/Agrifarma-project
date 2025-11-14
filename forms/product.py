from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, TextAreaField, SubmitField, IntegerField, FloatField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[
        DataRequired('Product name is required'),
        Length(min=3, max=255, message='Name must be between 3 and 255 characters')
    ])
    category = SelectField('Category', choices=[
        ('vegetables', '🥬 Vegetables'),
        ('fruits', '🍎 Fruits'),
        ('grains', '🌾 Grains'),
        ('dairy', '🥛 Dairy'),
        ('specialty', '🍯 Specialty Items'),
        ('inputs', '🧪 Farm Inputs')
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[
        DataRequired('Description is required'),
        Length(min=10, max=1000, message='Description must be between 10 and 1000 characters')
    ])
    price = FloatField('Price (Rs)', validators=[
        DataRequired('Price is required'),
        NumberRange(min=0, message='Price must be positive')
    ])
    quantity = IntegerField('Quantity Available', validators=[
        DataRequired('Quantity is required'),
        NumberRange(min=1, message='Quantity must be at least 1')
    ])
    location = StringField('Location', validators=[
        DataRequired('Location is required'),
        Length(min=3, max=255, message='Location must be between 3 and 255 characters')
    ])
    contact = StringField('Contact Number', validators=[
        DataRequired('Contact is required'),
        Length(min=10, max=20, message='Contact must be between 10 and 20 characters')
    ])
    product_image = FileField('Product Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')])
    terms = BooleanField('I agree to the marketplace terms and conditions', validators=[DataRequired()])
    submit = SubmitField('List Product')
