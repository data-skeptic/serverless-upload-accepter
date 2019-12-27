from chalice import Chalice, Response
from datetime import datetime
import base64
import filetype
import logging
import cgi
from io import BytesIO
import boto3
import time
import os


app = Chalice(app_name='Test')
app.debug = True
app.log.setLevel(logging.DEBUG)
app.api.binary_types.append("multipart/form-data")

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
        request_body = base64.b64decode(request_body)
    content_type_obj = app.current_request.to_dict()['headers']['content-type']
    content_type, property_dict = cgi.parse_header(content_type_obj)
    property_dict['boundary'] = property_dict['boundary'].encode('utf-8')
    property_dict['CONTENT-LENGTH'] = 123450000
    form_data = cgi.parse_multipart(BytesIO(request_body), property_dict)
    return form_data['file'][0]

def save_file_to_temp(file_data, file_name):
    full_path = '../{}'.format(file_name)
    with open(full_path, 'wb+') as f:
        f.write(file_data)
    return full_path

unix_timestamp_ms = lambda: int(round(time.time() * 1000))
get_file_name = lambda full_name: os.path.splitext(full_name)[0]

@app.route('/upload/{file_name}', methods=['POST'], cors=True, content_types=['multipart/form-data'])
def upload_file(file_name):
    # Form data pare to file
    print(app.current_request._body)
    parsed_file_data = ''
    try:
        parsed_file_data = parse_form_data()
        pass
    except:
        return Response(body={'error': 'Form Data parse error!'}, status_code=200)

    # # Save file to tmp folder
    # tmp_file_path = ''
    # try:
    #     tmp_file_path = save_file_to_temp(parsed_file_data, file_name)
    # except:
    #     return {'error': 'Save file to tmp folder error!'}

    # # Check file type
    # try:
    #     kind = filetype.guess(tmp_file_path)
    #     if kind.mime == 'application/pdf':
    #         return Response(body={'Success': 'This is a pdf'}, status_code=200)
    #     else:
    #         return Response(body={'Success': 'This is not a pdf'}, status_code=200)
    # except:
    #     return Response(body={'error': 'This is not a pdf'}, status_code=200)

    # Upload file to S3
    try:
        s3 = boto3.resource('s3')
        file_path = datetime.today().strftime('uploads/%Y/%m/%d/{}/{}.pdf').format(unix_timestamp_ms(), get_file_name(file_name))
        s3.Bucket(BUCKET).put_object(Key=file_path, Body=parsed_file_data)
        # return Response(body={'Success': 'Uploaded file to s3'}, status_code=200)

    except:
        return Response(body={'error': 'Save file to S3 error!'}, status_code=500)

    # # Check file type of s3
    # try:
    #     kind = filetype.guess(tmp_file_path)
    #     if kind.mime == 'application/pdf':
    #         return Response(body={'Success': 'This is a pdf'}, status_code=200)
    #     else:
    #         return Response(body={'Success': 'This is not a pdf'}, status_code=200)
    # except:
    #     return Response(body={'error': 'This is not a pdf'}, status_code=200)
