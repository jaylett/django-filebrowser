# coding: utf-8

# PYTHON IMPORTS
import os
import ntpath
import posixpath
import shutil

# DJANGO IMPORTS
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.encoding import filepath_to_uri

# FILEBROWSER IMPORTS
import filebrowser
from filebrowser.base import FileObject, FileListing
from filebrowser.sites import site

TESTS_PATH = os.path.dirname(os.path.abspath(__file__))
FILEBROWSER_PATH = os.path.split(TESTS_PATH)[0]


class FileObjectPathTests(TestCase):

    def setUp(self):
        """
        Save original values/functions so they can be restored in tearDown
        """
        self.original_directory = site.directory
        self.original_path = filebrowser.base.os.path

    def test_windows_paths(self):
        """
        Use ntpath to test windows paths independently from current os
        """
        site.directory = 'uploads/'
        filebrowser.base.os.path = ntpath
        f = FileObject('uploads\\testdir\\testfile.jpg', site=site)

        self.assertEqual(f.path_relative_directory, 'testdir\\testfile.jpg')
        self.assertEqual(f.dirname, r'testdir')

    def test_posix_paths(self):
        """
        Use posixpath to test posix paths independently from current os
        """
        filebrowser.base.os.path = posixpath
        site.directory = 'uploads/'
        f = FileObject('uploads/testdir/testfile.jpg', site=site)

        self.assertEqual(f.path_relative_directory, 'testdir/testfile.jpg')
        self.assertEqual(f.dirname, r'testdir')

    def tearDown(self):
        """
        Restore original values/functions
        """
        filebrowser.base.os.path = self.original_path
        site.directory = self.original_directory


class FileObjectUnicodeTests(TestCase):

    def setUp(self):
        """
        Save original values/functions so they can be restored in tearDown
        """
        self.original_path = filebrowser.base.os.path
        self.original_directory = site.directory

    def test_windows_paths(self):
        """
        Use ntpath to test windows paths independently from current os
        """
        site.directory = 'uploads/'
        filebrowser.base.os.path = ntpath
        f = FileObject('uploads\\$%^&*\\測試文件.jpg', site=site)

        self.assertEqual(f.path_relative_directory, '$%^&*\\測試文件.jpg')
        self.assertEqual(f.dirname, r'$%^&*')

    def test_posix_paths(self):
        """
        Use posixpath to test posix paths independently from current os
        """
        filebrowser.base.os.path = posixpath
        site.directory = 'uploads/'
        f = FileObject('uploads/$%^&*/測試文件.jpg', site=site)

        self.assertEqual(f.path_relative_directory, '$%^&*/測試文件.jpg')
        self.assertEqual(f.dirname, r'$%^&*')

    def tearDown(self):
        """
        Restore original values/functions
        """
        filebrowser.base.os.path = self.original_path
        site.directory = self.original_directory


class FileObjectAttributeTests(TestCase):

    def setUp(self):
        """
        Save original values/functions so they can be restored in tearDown

        We are using this folder structure (within storage.location):

        └── _versionstestdirectory
        └── fb_test_directory
            └── fb_tmp_dir
                └── fb_tmp_dir_sub
                    └── testimage.png

        """
        self.original_path = filebrowser.base.os.path
        self.original_directory = site.directory
        self.original_versions_basedir = filebrowser.base.VERSIONS_BASEDIR
        self.original_versions = filebrowser.base.VERSIONS
        self.original_admin_versions = filebrowser.base.ADMIN_VERSIONS

        # DIRECTORY
        # custom directory because this could be set with sites
        # and we cannot rely on filebrowser.settings
        self.directory = "fb_test_directory/"
        site.storage.makedirs(self.directory)
        # set site directory
        site.directory = self.directory

        # VERSIONS
        self.versions = "_versionstestdirectory"
        site.storage.makedirs(self.versions)

        # create temporary test folder
        self.tmpdir_name = posixpath.join(
            self.directory,
            "fb_tmp_dir",
            "fb_tmp_dir_sub",
        )
        site.storage.makedirs(self.tmpdir_name)

        # create alternative temporary test folder
        self.tmpdir_name_alt = posixpath.join(
            self.directory,
            "fb_tmp_dir",
            "fb_tmp_dir_sub",
            "xxx",
        )
        site.storage.makedirs(self.tmpdir_name_alt)

        # copy test image to temporary test folder
        self.image_path = os.path.join(
            FILEBROWSER_PATH,
            "static",
            "filebrowser",
            "img",
            "cancel.png",
        )
        with open(self.image_path, 'rb') as f:
            site.storage.save(
                posixpath.join(
                    self.tmpdir_name,
                    "testimage.png"
                ),
                f,
            )

        # set posixpath
        filebrowser.base.os.path = posixpath

        # fileobjects
        self.f_image = FileObject(os.path.join(self.tmpdir_name, "testimage.png"), site=site)
        self.f_folder = FileObject(os.path.join(self.tmpdir_name), site=site)
        self.f_folder_alt = FileObject(os.path.join(self.tmpdir_name_alt), site=site)

    def test_init_attributes(self):
        """
        FileObject init attributes

        # path
        # head
        # filename
        # filename_lower
        # filename_root
        # extension
        # mimetype
        """
        self.assertEqual(self.f_image.path, "fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimage.png")
        self.assertEqual(self.f_image.head, 'fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub')
        self.assertEqual(self.f_image.filename, 'testimage.png')
        self.assertEqual(self.f_image.filename_lower, 'testimage.png')
        self.assertEqual(self.f_image.filename_root, 'testimage')
        self.assertEqual(self.f_image.extension, '.png')
        self.assertEqual(self.f_image.mimetype, ('image/png', None))

    def test_general_attributes(self):
        """
        FileObject general attributes

        # filetype
        # filesize
        # date
        # datetime
        # exists
        """
        self.assertEqual(self.f_image.filetype, 'Image')
        self.assertEqual(self.f_image.filesize, 236)
        # FIXME: test date/datetime
        self.assertEqual(self.f_image.exists, True)

    def test_path_url_attributes(self):
        """
        FileObject path and url attributes

        # path (see init)
        # path_relative_directory
        # path_full
        # dirname
        # url
        """
        # test with image
        self.assertEqual(self.f_image.path, "fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimage.png")
        self.assertEqual(self.f_image.path_relative_directory, "fb_tmp_dir/fb_tmp_dir_sub/testimage.png")
        self.assertEqual(self.f_image.dirname, "fb_tmp_dir/fb_tmp_dir_sub")
        self.assertEqual(self.f_image.url, site.storage.url(self.f_image.path))

        # test with folder
        self.assertEqual(self.f_folder.path, "fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub")
        self.assertEqual(self.f_folder.path_relative_directory, "fb_tmp_dir/fb_tmp_dir_sub")
        self.assertEqual(self.f_folder.dirname, "fb_tmp_dir")
        self.assertEqual(self.f_folder.url, site.storage.url(self.f_folder.path))

        # test with alternative folder
        self.assertEqual(self.f_folder_alt.path, "fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/xxx")
        self.assertEqual(self.f_folder_alt.path_relative_directory, "fb_tmp_dir/fb_tmp_dir_sub/xxx")
        self.assertEqual(self.f_folder_alt.dirname, "fb_tmp_dir/fb_tmp_dir_sub")
        self.assertEqual(self.f_folder_alt.url, site.storage.url(self.f_folder_alt.path))

    def test_image_attributes(self):
        """
        FileObject image attributes

        # dimensions
        # width
        # height
        # aspectratio
        # orientation
        """
        self.assertEqual(self.f_image.dimensions, (16, 16))
        self.assertEqual(self.f_image.width, 16)
        self.assertEqual(self.f_image.height, 16)
        self.assertEqual(self.f_image.aspectratio, 1.0)
        self.assertEqual(self.f_image.orientation, 'Landscape')

    def test_folder_attributes(self):
        """
        FileObject folder attributes

        # directory (deprecated)
        # folder (deprecated)
        # is_folder
        # is_empty
        """
        # test with image
        self.assertEqual(self.f_image.is_folder, False)
        self.assertEqual(self.f_image.is_empty, False)

        # test with folder
        self.assertEqual(self.f_folder.is_folder, True)
        self.assertEqual(self.f_folder.is_empty, False)

        # test with alternative folder
        self.assertEqual(self.f_folder_alt.is_folder, True)
        self.assertEqual(self.f_folder_alt.is_empty, True)

    def test_version_attributes_1(self):
        """
        FileObject version attributes/methods
        without versions_basedir

        # is_version
        # original
        # original_filename
        # versions_basedir
        # versions
        # admin_versions
        # version_name(suffix)
        # version_path(suffix)
        # version_generate(suffix)
        """
        # new settings
        filebrowser.base.VERSIONS_BASEDIR = ""
        filebrowser.base.VERSIONS = {
            'admin_thumbnail': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
            'large': {'verbose_name': 'Large', 'width': 600, 'height': '', 'opts': ''},
        }
        filebrowser.base.ADMIN_VERSIONS = ['large']
        # expected test results
        version_list = ['fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimage_admin_thumbnail.png', 'fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.png',]
        admin_version_list = ['fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.png']

        self.assertEqual(self.f_image.is_version, False)
        self.assertEqual(self.f_image.original.path, self.f_image.path)
        self.assertEqual(self.f_image.versions_basedir, "fb_test_directory/")
        self.assertEqual(self.f_image.versions(), version_list)
        self.assertEqual(self.f_image.admin_versions(), admin_version_list)
        self.assertEqual(self.f_image.version_name("large"), "testimage_large.png")
        self.assertEqual(self.f_image.version_path("large"), "fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.png")

        # version does not exist yet
        f_version = FileObject(os.path.join(self.directory, self.tmpdir_name, "testimage_large.png"), site=site)
        self.assertEqual(f_version.exists, False)
        # generate version
        f_version = self.f_image.version_generate("large")
        self.assertEqual(f_version.path, "fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.png")
        self.assertEqual(f_version.exists, True)
        self.assertEqual(f_version.is_version, True)
        self.assertEqual(f_version.original_filename, "testimage.png")
        self.assertEqual(f_version.original.path, self.f_image.path)
        # FIXME: versions should not have versions or admin_versions

    def test_version_attributes_2(self):
        """
        FileObject version attributes/methods
        with versions_basedir

        # is_version
        # original
        # original_filename
        # versions_basedir
        # versions
        # admin_versions
        # version_name(suffix)
        # version_generate(suffix)
        """
        # new settings
        filebrowser.base.VERSIONS_BASEDIR = "fb_test_directory/_versions"
        filebrowser.base.VERSIONS = {
            'admin_thumbnail': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
            'large': {'verbose_name': 'Large', 'width': 600, 'height': '', 'opts': ''},
        }
        filebrowser.base.ADMIN_VERSIONS = ['large']
        # expected test results
        version_list = ['fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_admin_thumbnail.png', 'fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.png']
        admin_version_list = ['fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.png']

        self.assertEqual(self.f_image.is_version, False)
        self.assertEqual(self.f_image.original.path, self.f_image.path)
        self.assertEqual(self.f_image.versions_basedir, "fb_test_directory/_versions")
        self.assertEqual(self.f_image.versions(), version_list)
        self.assertEqual(self.f_image.admin_versions(), admin_version_list)
        self.assertEqual(self.f_image.version_name("large"), "testimage_large.png")
        self.assertEqual(self.f_image.version_path("large"), "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.png")

        # version does not exist yet
        f_version = FileObject(os.path.join(self.directory, self.tmpdir_name, "testimage_large.png"), site=site)
        self.assertEqual(f_version.exists, False)
        # generate version
        f_version = self.f_image.version_generate("large")
        self.assertEqual(f_version.path, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.png")
        self.assertEqual(f_version.exists, True)
        self.assertEqual(f_version.is_version, True)
        self.assertEqual(f_version.original_filename, "testimage.png")
        self.assertEqual(f_version.original.path, self.f_image.path)
        self.assertEqual(f_version.versions(), [])
        self.assertEqual(f_version.admin_versions(), [])

    def test_version_attributes_3(self):
        """
        FileObject version attributes/methods
        with alternative versions_basedir

        # is_version
        # original
        # original_filename
        # versions_basedir
        # versions
        # admin_versions
        # version_name(suffix)
        # version_generate(suffix)
        """
        # new settings
        filebrowser.base.VERSIONS_BASEDIR = "_versionstestdirectory"
        filebrowser.base.VERSIONS = {
            'admin_thumbnail': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
            'large': {'verbose_name': 'Large', 'width': 600, 'height': '', 'opts': ''},
        }
        filebrowser.base.ADMIN_VERSIONS = ['large']
        # expected test results
        version_list = ['_versionstestdirectory/fb_tmp_dir/fb_tmp_dir_sub/testimage_admin_thumbnail.png', '_versionstestdirectory/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.png']
        admin_version_list = ['_versionstestdirectory/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.png']

        self.assertEqual(self.f_image.is_version, False)
        self.assertEqual(self.f_image.original.path, self.f_image.path)
        self.assertEqual(self.f_image.versions_basedir, "_versionstestdirectory")
        self.assertEqual(self.f_image.versions(), version_list)
        self.assertEqual(self.f_image.admin_versions(), admin_version_list)
        self.assertEqual(self.f_image.version_name("large"), "testimage_large.png")
        self.assertEqual(self.f_image.version_path("large"), "_versionstestdirectory/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.png")

        # version does not exist yet
        f_version = FileObject(os.path.join(self.directory, self.tmpdir_name, "testimage_large.png"), site=site)
        self.assertEqual(f_version.exists, False)
        # generate version
        f_version = self.f_image.version_generate("large")
        self.assertEqual(f_version.path, "_versionstestdirectory/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.png")
        self.assertEqual(f_version.exists, True)
        self.assertEqual(f_version.is_version, True)
        self.assertEqual(f_version.original_filename, "testimage.png")
        self.assertEqual(f_version.original.path, self.f_image.path)
        self.assertEqual(f_version.versions(), [])
        self.assertEqual(f_version.admin_versions(), [])

    def test_delete(self):
        """
        FileObject delete methods

        # delete
        # delete_versions
        # delete_admin_versions
        """

        # new settings
        filebrowser.base.VERSIONS_BASEDIR = ""
        filebrowser.base.VERSIONS = {
            'admin_thumbnail': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
            'large': {'verbose_name': 'Large', 'width': 600, 'height': '', 'opts': ''},
        }
        filebrowser.base.ADMIN_VERSIONS = ['large']

        # version does not exist yet
        f_version = FileObject(os.path.join(self.directory, self.tmpdir_name, "testimage_large.png"), site=site)
        self.assertEqual(f_version.exists, False)
        # generate version
        f_version = self.f_image.version_generate("large")
        f_version_thumb = self.f_image.version_generate("admin_thumbnail")
        self.assertEqual(f_version.exists, True)
        self.assertEqual(f_version_thumb.exists, True)
        self.assertEqual(f_version.path, "fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.png")
        self.assertEqual(f_version_thumb.path, "fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimage_admin_thumbnail.png")

        # delete admin versions (large)
        self.f_image.delete_admin_versions()
        self.assertEqual(site.storage.exists(f_version.path), False)

        # delete versions (admin_thumbnail)
        self.f_image.delete_versions()
        self.assertEqual(site.storage.exists(f_version_thumb.path), False)

    def tearDown(self):
        """
        Restore original values/functions
        """

        site.storage.rmtree(self.directory)
        site.storage.rmtree(self.versions)

        filebrowser.base.os.path = self.original_path
        site.directory = self.original_directory
        filebrowser.base.VERSIONS_BASEDIR = self.original_versions_basedir
        filebrowser.base.VERSIONS = self.original_versions
        filebrowser.base.ADMIN_VERSIONS = self.original_admin_versions


class FileListingTests(TestCase):

    def setUp(self):
        """
        Save original values/functions so they can be restored in tearDown

        our temporary file structure looks like this:

        /fb_test_directory/
        /fb_test_directory/testimage.png
        /fb_test_directory/fb_tmp_dir/
        /fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/
        /fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimage.png
        """
        self.original_path = filebrowser.base.os.path
        self.original_directory = site.directory
        self.original_versions_basedir = filebrowser.base.VERSIONS_BASEDIR
        self.original_versions = filebrowser.base.VERSIONS
        self.original_admin_versions = filebrowser.base.ADMIN_VERSIONS

        # DIRECTORY
        # custom directory because this could be set with sites
        # and we cannot rely on filebrowser.settings
        # FIXME: find better directory name
        self.directory = "fb_test_directory/"
        site.storage.makedirs(self.directory)
        # set site directory
        site.directory = self.directory

        # create temporary test folder and move testimage
        # FIXME: find better path names
        self.tmpdir_name = posixpath.join(self.directory, "fb_tmp_dir", "fb_tmp_dir_sub")
        site.storage.makedirs(self.tmpdir_name)

        # copy test image to temporary test folder
        self.image_path = os.path.join(FILEBROWSER_PATH, "static", "filebrowser", "img", "cancel.png")
        with open(self.image_path, 'rb') as f:
            site.storage.save(posixpath.join(self.directory, "testimage.png"), f)
        with open(self.image_path, 'rb') as f:
            site.storage.save(posixpath.join(self.tmpdir_name, "testimage.png"), f)

        # set posixpath
        filebrowser.base.os.path = posixpath

        # filelisting/fileobject
        self.f_listing = FileListing(self.directory, sorting_by='date', sorting_order='desc')
        self.f_listing_file = FileListing(os.path.join(self.directory, self.tmpdir_name, "testimage.png"))

    def test_init_attributes(self):
        """
        FileListing init attributes

        # path
        # filter_func
        # sorting_by
        # sorting_order
        """
        self.assertEqual(self.f_listing.path, 'fb_test_directory/')
        self.assertEqual(self.f_listing.filter_func, None)
        self.assertEqual(self.f_listing.sorting_by, 'date')
        self.assertEqual(self.f_listing.sorting_order, 'desc')

    def test_listing(self):
        """
        FileObject listing

        # listing
        # files_listing_total
        # files_listing_filtered
        # results_listing_total
        # results_listing_filtered
        """
        self.assertEqual(self.f_listing_file.listing(), [])
        self.assertEqual(list(self.f_listing.listing()), [u'fb_tmp_dir', u'testimage.png'])
        self.assertEqual(list(f.path for f in self.f_listing.files_listing_total()), [u'fb_test_directory/testimage.png', u'fb_test_directory/fb_tmp_dir'])
        self.assertEqual(list(f.path for f in self.f_listing.files_listing_filtered()), [u'fb_test_directory/testimage.png', u'fb_test_directory/fb_tmp_dir'])
        self.assertEqual(self.f_listing.results_listing_total(), 2)
        self.assertEqual(self.f_listing.results_listing_filtered(), 2)

    def test_listing_filtered(self):
        """
        FileObject listing

        # listing
        # files_listing_total
        # files_listing_filtered
        # results_listing_total
        # results_listing_filtered
        """
        self.assertEqual(self.f_listing_file.listing(), [])
        self.assertEqual(list(self.f_listing.listing()), [u'fb_tmp_dir', u'testimage.png'])
        self.assertEqual(list(f.path for f in self.f_listing.files_listing_total()), [u'fb_test_directory/testimage.png', u'fb_test_directory/fb_tmp_dir'])
        self.assertEqual(list(f.path for f in self.f_listing.files_listing_filtered()), [u'fb_test_directory/testimage.png', u'fb_test_directory/fb_tmp_dir'])
        self.assertEqual(self.f_listing.results_listing_total(), 2)
        self.assertEqual(self.f_listing.results_listing_filtered(), 2)

    def test_walk(self):
        """
        FileObject walk

        # walk
        # files_walk_total
        # files_walk_filtered
        # results_walk_total
        # results_walk_filtered
        """
        self.assertEqual(self.f_listing_file.walk(), [])
        self.assertEqual(list(self.f_listing.walk()), [u'fb_tmp_dir/fb_tmp_dir_sub/testimage.png', u'fb_tmp_dir/fb_tmp_dir_sub', u'fb_tmp_dir', u'testimage.png'])
        self.assertEqual(list(f.path for f in self.f_listing.files_walk_total()),  [u'fb_test_directory/testimage.png', u'fb_test_directory/fb_tmp_dir', u'fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub', u'fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimage.png'])
        self.assertEqual(list(f.path for f in self.f_listing.files_walk_filtered()),  [u'fb_test_directory/testimage.png', u'fb_test_directory/fb_tmp_dir', u'fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub', u'fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimage.png'])
        self.assertEqual(self.f_listing.results_walk_total(), 4)
        self.assertEqual(self.f_listing.results_walk_filtered(), 4)

    def tearDown(self):
        """
        Restore original values/functions
        """

        site.storage.rmtree(self.directory)

        filebrowser.base.os.path = self.original_path
        site.directory = self.original_directory
        filebrowser.base.VERSIONS_BASEDIR = self.original_versions_basedir
        filebrowser.base.VERSIONS = self.original_versions
        filebrowser.base.ADMIN_VERSIONS = self.original_admin_versions
