from datetime import datetime 
from datetime import datetime


end_date = datetime.strptime('01-06-2022', '%d-%m-%Y')
if datetime.today() > end_date:
    print('pass')
else:
    print('wrong')