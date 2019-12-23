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
                <form action="#" method="post" id="frm" enctype="multipart/form-data">
                        Select File to upload:
                        <input type="file" name="fileToUpload" id="fileToUpload">
                        <input type="submit" value="Upload Image" id="sbmit" name="submit" disabled>
                </form>
                </body>
                <script>
				document.getElementById('fileToUpload').addEventListener("change", changeAction);
				const frm = document.getElementById('frm');
				const sbmit = document.getElementById('sbmit');
				function changeAction(e){
					frm.action = "/api/upload/" + e.target.files[0].name;
					sbmit.disabled = !(e.target.files[0].name);
				}
				</script>
                </html>"""
    return Response(template, status_code=200, headers={"Content-Type": "text/html", "Access-Control-Allow-Origin": "*"})
