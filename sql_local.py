import pg8000

def fetch_data():
    return pg8000.connect(
        host='localhost',        
        database='*****',
        user='******',
        password='******'
    )
