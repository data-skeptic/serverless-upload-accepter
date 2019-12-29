from chalice import Chalice, Response
from datetime import datetime
import base64
import filetype
import cgi
from io import BytesIO
import boto3
import time
import os
import urllib.request


# Config ->
BUCKET=''
ACCESS_KEY_ID = ''
SECRET_ACCESS_KEY = ''
# <- Config

s3_client = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=SECRET_ACCESS_KEY
)

app = Chalice(app_name='Test')

app.api.binary_types.append("multipart/form-data")

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
    full_path = '/tmp/{}'.format(file_name)
    with open(full_path, 'wb+') as f:
        f.write(file_data)
    return full_path

def create_presigned_url(bucket_name, object_name, expiration=3600):

    s3_client = boto3.client(
        's3',
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY
    )
    response = s3_client.generate_presigned_url('get_object',
                                                Params={'Bucket': bucket_name,
                                                        'Key': object_name},
                                                ExpiresIn=expiration)
    return response



unix_timestamp_ms = lambda: int(round(time.time() * 1000))
get_file_name = lambda full_name: os.path.splitext(full_name)[0]

def get_file_type_from_blob(blob_data):
    # # Save file to tmp folder
    tmp_file_path = save_file_to_temp(blob_data, 'temp.dmp')
    # # Check file type
    kind = filetype.guess(tmp_file_path)
    return kind

@app.route('/upload/{file_name}', methods=['POST'], cors=True, content_types=['multipart/form-data'])
def upload_file(file_name):
    # Form data pare to file
    parsed_file_data = ''
    try:
        parsed_file_data = parse_form_data()
        pass
    except:
        return Response(body={'error': 'Form Data parse error!'}, status_code=200)

    # # Check file type
    try:
        kind = get_file_type_from_blob(parsed_file_data)
    except:
        return Response(body={'error': 'unknown file!'}, status_code=200)


    # Upload file to S3
    try:
        file_key = datetime.today().strftime('uploads/%Y/%m/%d/{}/{}.pdf').format(unix_timestamp_ms(), get_file_name(file_name))
        s3_client.put_object(Bucket = BUCKET, Key = file_key, Body = parsed_file_data, ContentType = kind.mime)
        pass
    except:
        return Response(body={'error': 'Save file to S3 error!'}, status_code=500)

    # Check file type of s3

    try:
        s3object_url = create_presigned_url(BUCKET, file_key, 1200)
        response = urllib.request.urlopen(s3object_url)
        raw_data = response.read()

        kind = get_file_type_from_blob(raw_data)
        if kind.mime == 'image/png':
            return Response(body={'Success': 'This is a png'}, status_code=200)
        else:
            return Response(body={'Success': 'This is not a png'}, status_code=200)

    except:
        return Response(body={'error': 'This is not a png'}, status_code=200)
