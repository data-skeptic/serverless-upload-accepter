from chalice import Chalice

app = Chalice(app_name='Test')


@app.route('/')
def index():
    return {'hello': 'world'}
