# Home Library

Project for Internet Applications course at Poznan University of Technology.

## Getting Started

### Clone the repository
```
git clone https://github.com/Nuurek/HomeLibrary.git
```

### Install requirements
```
cd HomeLibrary
pip install -r requirements.txt
```

### Migrate database
```
python manage.py migrate
```

### Run server using either manage.py...
```
python manage.py runserver
```

### ...or gunicorn
```
gunicorn home_library.wsgi
```

## Deployment

### Settings
```home_library.settings``` defines local and production settings. To choose a specific one set ```DJANGO_SETTINGS_MODULE``` environment variable.
Default: ```home_library.settings.local```

### Database
Production uses postgreSQL. To connect with a DB set ```DATABASE_URL``` that points to database.

### Storage
Static and media files are stored in Amazon S3. Production uses django-storages and botos3 modules. Create the storage and set following: ```AWS_ACCESS_KEY_ID```, ```AWS_SECRET_ACCESS_KEY```, ```AWS_STORAGE_BUCKET_NAME```, ```AWS_USER_ARN```

### Emails
Emails are sent through SentGrid. Proper values of envs: ```SENDGRID_USERNAME```, ```SENDGRID_PASSWORD``` have to be set.

### Google Books API
Searching external books is implemented with Google Books service. Authentication requires setting ```GOOGLE_BOOKS_API_KEY```

### Secret key
As every Django app this one also uses ```SECRET_KEY```. You have to set it as an environmental variable. **DO NOT JUST COPY IT FROM LOCAL SETTINGS FILE**.

### Debbuging
To debug production set ```DEBUG```

## Disclosure
I've decided to use Django because it is the framework I got the most experience in. It was a mistake. It's 2017 - I should develop backend and frontend separately for such a kind of web app.