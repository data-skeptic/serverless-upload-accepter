from chalice import Chalice, Response
import filetype
import logging
import json
import gzip
import cgi
from io import BytesIO

app = Chalice(app_name='Test')
app.debug = True
app.log.setLevel(logging.DEBUG)

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
                <script>
				document.getElementById('fileToUpload').addEventListener("change", changeAction);
				const sbmit = document.getElementById('sbmit');
				function changeAction(e){
					sbmit.disabled = !(e.target.files[0].name);
				}
				</script>
                </html>"""
    return Response(template, status_code=200, headers={"Content-Type": "text/html", "Access-Control-Allow-Origin": "*"})

def _get_parts():
    rfile = BytesIO(app.current_request.raw_body)
    content_type = app.current_request.headers['content-type']
    _, parameters = cgi.parse_header(content_type)
    parameters['boundary'] = parameters['boundary'].encode('utf-8')
    parsed = cgi.parse_multipart(rfile, parameters)
    return parsed

@app.route('/upload', methods=['POST'], content_types=['multipart/form-data'])
def upload_body():
    files = _get_parts()
    print(files)
    return {k: v[0].decode('utf-8') for (k, v) in files.items()}