from chalice import Chalice, Response
import filetype
import logging
import json
import cgi
from io import BytesIO
import codecs
import boto3

s3_client = boto3.client('s3')
BUCKET = 'sebastian-testbucket'

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
                        <input type="file" name="file" id="fileToUpload">
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
    parameters['CONTENT-LENGTH'] = 200000
    parsed = cgi.parse_multipart(rfile, parameters)
    return parsed



@app.route('/upload', methods=['POST'], content_types=['multipart/form-data'])
def upload_file():
    files = _get_parts()

    with open('/tmp/test.png', 'wb') as tmp_file:
        tmp_file.write(files["file"][0])
    kind = filetype.guess('/tmp/test.png')

    s3_client.upload_file('/tmp/test.png', BUCKET, 'test.png')
    return {"file": json.dumps(kind)}

    # app.log.debug(files)
    # return {"file": files["file"][0].decode('utf-8')}