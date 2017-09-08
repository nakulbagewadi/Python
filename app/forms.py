from flask_wtf import Form
from wtforms import RadioField
from wtforms.validators import DataRequired
    

class ClubIndexForm(Form):
	clubs = RadioField('Clubs', choices = [	('Liverpool','Liverpool'), ('Chelsea','Chelsea'),
											('Arsenal','Arsenal'), 
											('Manchester United','Manchester United'),
											('Manchester City','Manchester City'), 
											('Tottenham Hotspur','Tottenham Hotspur')],
											validators = [DataRequired()])
	
	years = RadioField('Years', choices = [	('2016','Last year'), 
											('2016,2015','Last 2 years'), 
											('2016,2015,2014','Last 3 years'), 
											('2016,2015,2014,2013','Last 4 years'), 
											('2016,2015,2014,2013,2012', 'Last 5 years'),
											('2016,2015,2014,2013,2012,2011', 'Last 6 years'),
											('2016,2015,2014,2013,2012,2011,2010', 'Last 7 years')],
											validators = [DataRequired()])
											

class StatisticsForm(Form):
    pass