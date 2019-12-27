from chalice import Chalice, Response
import filetype
import logging
import cgi
from io import BytesIO
import boto3

app = Chalice(app_name='Test')
app.debug = True
app.log.setLevel(logging.DEBUG)

s3_client = boto3.client('s3')
BUCKET = 'sebastian-testbucket'

@app.route('/', cors=True)
def index():
    return {'hello': 'world'}

@app.route('/upload')
def upload():
    template = """<!DOCTYPE html>
                <html>
                <body>
                <form action="#" method="post" id="frm" enctype="multipart/form-data">
                        Select File to upload:
                        <input type="file" name="file" id="fileToUpload">
                        <input type="submit" value="Upload Image" id="sbmit" name="submit" disabled>
                </form>
                </body>
                <script>
				document.getElementById('fileToUpload').addEventListener("change", changeAction);
				const sbmit = document.getElementById('sbmit');
				const frm = document.getElementById('frm');
				function changeAction(e){
					sbmit.disabled = !(e.target.files[0].name);
                    frm.action = "/api/upload/" + e.target.files[0].name;
				}
				</script>
                </html>"""
    return Response(template, status_code=200, headers={"Content-Type": "text/html", "Access-Control-Allow-Origin": "*"})

def parse_form_data():
    request_body = app.current_request._body
    if isinstance(request_body, str):
        request_body = request_body.encode()
    content_type_obj = app.current_request.to_dict()['headers']['content-type']
    content_type, property_dict = cgi.parse_header(content_type_obj)
    property_dict['boundary'] = property_dict['boundary'].encode('utf-8')
    property_dict['CONTENT-LENGTH'] = 123450000
    form_data = cgi.parse_multipart(BytesIO(request_body), property_dict)
    return form_data['file'][0]

def save_file_to_temp(file_data, file_name):
    full_path = '/tmp/{}'.format(file_name)
    with open(full_path, 'wb+') as f:
        f.write(file_data)
    return full_path


@app.route('/upload/{file_name}', methods=['POST'], cors=True, content_types=['multipart/form-data'])
def upload_file(file_name):
    # Form data pare to file
    parsed_file_data = ''
    try:
        parsed_file_data = parse_form_data()
        pass
    except:
        return Response(body={'error': 'Form Data parse error!'}, status_code=200)

    # Save file to tmp folder
    tmp_file_path = ''
    try:
        tmp_file_path = save_file_to_temp(parsed_file_data, file_name)
    except:
        return {'error': 'Save file to tmp folder error!'}

    # Check file type
    try:
        kind = filetype.guess(tmp_file_path)
        if kind.mime == 'application/pdf':
            return Response(body={'Success': 'This is a pdf'}, status_code=200)
        else:
            return Response(body={'Success': 'This is not a pdf'}, status_code=200)
    except:
        return Response(body={'error': 'This is not a pdf'}, status_code=200)
