import os.path
import subprocess
import sys

import django
from django.conf import settings

AWS_STORAGE_BUCKET_NAME=os.environ.get('AWS_STORAGE_BUCKET_NAME')
THIS_DIR=os.path.dirname(os.path.dirname(__file__))
if AWS_STORAGE_BUCKET_NAME is None:
    DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage'
else:
    DEFAULT_FILE_STORAGE='test_s3backend.S3Storage'

settings.configure(
    DEBUG=True,
    INSTALLED_APPS=[
        'filebrowser',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.admin',
    ],
    SECRET_KEY='empty',
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'test',
        },
    },
    MIDDLEWARE_CLASSES=(
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ),
    ROOT_URLCONF='test_urls',
    DEFAULT_FILE_STORAGE=DEFAULT_FILE_STORAGE,
    AWS_STORAGE_BUCKET_NAME=AWS_STORAGE_BUCKET_NAME,
    AWS_ACCESS_KEY_ID=os.environ.get('AWS_ACCESS_KEY_ID'),
    AWS_SECRET_ACCESS_KEY=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    AWS_PRELOAD_METADATA=True,
    AWS_QUERYSTRING_AUTH=False,
    MEDIA_ROOT=os.path.join(THIS_DIR, 'test_media'),
    FILEBROWSER_VERSIONS_BASEDIR='_versions/',
    FILEBROWSER_DIRECTORY='uploads/',
)

if hasattr(django, 'setup'):
    django.setup()

def ensuredir(d):
    if not os.path.exists(d):
        os.mkdir(d)

ensuredir(settings.MEDIA_ROOT)
ensuredir(os.path.join(settings.MEDIA_ROOT, settings.FILEBROWSER_VERSIONS_BASEDIR))
ensuredir(os.path.join(settings.MEDIA_ROOT, settings.FILEBROWSER_DIRECTORY))

try:
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner(verbosity=1, failfast=False)
    if len(sys.argv) > 1:
        to_run = sys.argv[1:]
    else:
        to_run = ['filebrowser', ]
    failures = test_runner.run_tests(to_run)
    if failures: #pragma no cover
        sys.exit(failures)
finally:
    os.system("rm -rf %s" % settings.MEDIA_ROOT) # oh so insecure
