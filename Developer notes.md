<h2>Developer Notes</h2>
<hr>
<li>Staticfiles are served from S3 so changes in project are reflected only when
static files are updated in S3</li>
<li>Run collectstatic for the same after every change in CSS, JS</li>
<li>Differences between how static file and media file are uploaded can be found in storages.py</li>
<li></li>
<li></li>
<li></li>
<li></li>

DatasetReader(path, driver=None, sharing=None)
path = parse_path('https://demdembucket.s3.amazonaws.com/media/icrisat/ortho/20221028/c27648a1-3fc1-4258-906a-6ba46860f6cc.jpg')