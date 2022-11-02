<h1>Crop Analysis</h1>
<hr>
<p>Crop Analysis is a web application dashboard for uploading hyperspectral images and viewing
them in a google map layout</p>

<h2>Installing</h2>
<hr>
<ul>
<li>Download the zip and enter the main directory.</li>
<li>Install the mentioned packages in requirements.txt.</li>
<li>Add the necessary inputs related to AWS in aws_settings.py.</li>
<li>In the S3 bucket, unblock all public access, enable ACL and public read for objects and
add CORS usage appropriately.</li>
<li>Run python manage.py migrate to create the necessary tables in the db.</li>
<li>Create a superuser for admin purposes.</li>
<li>Run python manage.py runserver in the terminal and open to link in browser.</li>
<li>Currently there is no API for creating users, custom users and clients.</li>
<li>Create user, then client and then custom user to connect the client and the user.</li>
<li>There are no APIs to edit or delete images/objects from the db, all permissions are available
only for the admin users.</li>
</ul>

<h2>Usage</h2>
<hr>
<ul>
<li>Open the link in terminal and enter the credentials for the user.</li>
<li>Once redirected to the dashboard, to add new images, click add images in the top left.</li>
<li>Click choose file button in the form and upload.</li>
<li>File will be uploaded with UUID name and directory as mentioned in the code.</li>
<li>Page will automatically redirect to map page with an option to cancel.</li>
<li>You can go to dashboard page to view all the images currently uploaded by the 
specific user with a direct link to map page layout for all.</li>
</ul>