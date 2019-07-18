from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

'''
使用WTF实现表单
'''
class Search(FlaskForm):
    search = StringField(' ',validators=[DataRequired( )])
    submit = SubmitField(u'go!')

