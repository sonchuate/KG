from datetime import datetime

now = datetime.now()
current_month = now.month
current_year = now.year

def cal_exp(st:str, et:str)->float:
    """format: mon:year"""
    try: 
        m1,y1 = st.split(':')
        if et.strip('"').strip("'").startswith('now'):
            m2,y2 = current_month, current_year
        else:
            m2,y2 = et.split(':')
            
        return int(y2.strip()) - int(y1.strip()) +\
             int(m2.strip())/12.0 - int(m1.strip())/12.0
    except:
        pass

    return 0