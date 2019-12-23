from chalice import Chalice, Response
import codecs
app = Chalice(app_name='Test')


@app.route('/')
def index():
    return {'hello': 'world'}

@app.route('/upload')
def upload():
    template = """<!DOCTYPE html>
                <html>
                <body>
                <form action="/api/upload" method="post" id="frm" enctype="multipart/form-data">
                        Select File to upload:
                        <input type="file" name="fileToUpload" id="fileToUpload">
                        <input type="submit" value="Upload Image" id="sbmit" name="submit" disabled>
                </form>
                </body>
                </html>"""
    return Response(template, status_code=200, headers={"Content-Type": "text/html", "Access-Control-Allow-Origin": "*"})
