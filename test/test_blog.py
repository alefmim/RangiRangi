# project/test_basic.py
#!/usr/bin/python3

import os
import unittest
import datetime

from urllib.request import Request
from flask_testing import TestCase
from flask import session
from blog import *
from blog.app import *


class BlogTests(TestCase):
    def create_app(self):
        '''Creates and configures an instance of the Flask application.'''
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.secret_key = os.urandom(32)
        limiter.enabled = False
        self.app = app.test_client()
        self.assertEqual(app.debug, False)
        return app

    def setUp(self):
        self.db = SQLAlchemy(app)
        db.drop_all()
        db.create_all()

    def make_config_file(self):
        session['logged_in'] = True
        # Create a new config
        newconfig = {}
        # Assign default values to our configuration
        newconfig['title'] = 'Blog Title'
        newconfig['desc'] = 'Blog Description'
        newconfig['dispname'] = tr('Admin')
        newconfig['mailaddr'] = 'test@test.com'
        newconfig['ppp'] = 10
        newconfig['dtformat'] = '%Y %B %d'
        newconfig['calendar'] = 'Jalali'
        newconfig['autoapproval'] = 'No'
        newconfig['disablecomments'] = 'No'
        # Save the default password (md5 hash of 'admin') in our new config
        newpwd = hashlib.md5('admin'.encode('utf-8'))
        newconfig['pwd'] = newpwd.hexdigest()
        # Create a config file using our new config
        saveConfig(newconfig)

    def login(self):
        self.make_config_file()
        response = self.client.post('/login',
                                    data=dict(pwd='admin'),
                                    follow_redirects=True)
        return response

    def logout(self):
        response = self.client.get('/logout', follow_redirects=False)
        return response

    ###############
    #### Tests ####
    ###############

    def test_installation(self):
        if os.path.isfile(CONFIG_FILE):
            os.remove(CONFIG_FILE)
        response = self.client.get('/')
        self.assertRedirects(response, url_for('config'))
        response = self.client.get('/config')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'admin', response.data)
        self.assertIn(b'%Y %B %d', response.data)
        self.assertIn(b'Jalali', response.data)

    def test_main_page_admin(self):
        self.make_config_file()
        self.logout()
        response = self.client.get('/')
        self.assertEqual(request.path, url_for('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(session['logged_in'], True)
        self.assertIn(b'Blog Title', response.data)
        self.assertIn(b'Blog Description', response.data)
        self.assertIn(b'test@test.com', response.data)

    def test_main_page_user(self):
        with self.client:
            self.make_config_file()
            self.logout()
            response = self.client.get('/')
            self.assertEqual(request.path, url_for('index'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(session['logged_in'], False)
            self.assertIn(b'Blog Title', response.data)
            self.assertIn(b'Blog Description', response.data)
            self.assertIn(b'test@test.com', response.data)

    def test_login(self):
        with self.client:
            response = self.login()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(session['logged_in'], True)

    def test_logout(self):
        with self.client:
            response = self.client.get('/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(session['logged_in'], False)
            self.login()
            response = self.logout()
            self.assertEqual(response.status_code, 302)
            self.assertNotIn('logged_in', session)

    def test_invalid_login(self):
        with self.client:
            self.make_config_file()
            self.logout()
            response = self.client.post('/login',
                                        data=dict(pwd='nimda'),
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(session['logged_in'], False)

    def test_newcategory(self):
        with self.client:
            self.login()
            response = self.client.post('/newcategory',
                                        data=json.dumps(
                                            dict(name='anothercategory')),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            cat = dbcategory.query.filter(
                dbcategory.name == 'anothercategory').first()
            self.assertIsNotNone(cat)

    def test_editcategory(self):
        with self.client:
            self.login()
            # Create a new category first
            category = dbcategory('Other', 0)
            db.session.add(category)
            db.session.commit()
            response = self.client.post('/editcategory',
                                        data=json.dumps(
                                            dict(id=1, name='editedcategory')),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            cat = dbcategory.query.filter(dbcategory.catid == 1).first()
            self.assertIsNotNone(cat)
            self.assertEqual(cat.name, 'editedcategory')

    def test_removecategory_nopost(self):
        with self.client:
            self.login()
            # Create a new category first
            category = dbcategory('removeme', 0)
            db.session.add(category)
            db.session.commit()
            response = self.client.post('/removecategory',
                                        data=json.dumps(dict(id=1)),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            cat = dbcategory.query.filter(
                dbcategory.name == 'removeme').first()
            self.assertIsNone(cat)

    def test_removecategory(self):
        with self.client:
            self.login()
            # Create a new category first
            category = dbcategory('removeme', 0)
            db.session.add(category)
            # Add a post to new category
            post = dbpost(
                'title', 'content',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 1,
                '', 0)
            db.session.add(post)
            db.session.commit()
            response = self.client.post('/removecategory',
                                        data=json.dumps(dict(id=1)),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            cat = dbcategory.query.filter(
                dbcategory.name == 'removeme').first()
            post = dbpost.query.filter(dbpost.postid == 1).first()
            self.assertIsNone(cat)
            self.assertIsNone(post)

    def test_invalid_removecategory_noid(self):
        with self.client:
            self.login()
            # Create a new category first
            category = dbcategory('removeme', 0)
            db.session.add(category)
            db.session.commit()
            response = self.client.post('/removecategory',
                                        data=json.dumps(dict()),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 400)
            cat = dbcategory.query.filter(
                dbcategory.name == 'removeme').first()
            self.assertIsNotNone(cat)

    def test_invalid_removecategory_id(self):
        with self.client:
            self.login()
            # Create a new category first
            category = dbcategory('removeme', 0)
            db.session.add(category)
            db.session.commit()
            response = self.client.post('/removecategory',
                                        data=json.dumps(dict(id=10)),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 400)
            cat = dbcategory.query.filter(
                dbcategory.name == 'removeme').first()
            self.assertIsNotNone(cat)

    def test_addlink(self):
        with self.client:
            self.login()
            response = self.client.post('/addlink',
                                        data=json.dumps(
                                            dict(name='newlink',
                                                 address='http://link.com')),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            lnk = dblink.query.filter(dblink.name == 'newlink').first()
            self.assertIsNotNone(lnk)

    def test_invalid_addlink_nonameaddr(self):
        with self.client:
            self.login()
            response = self.client.post('/addlink',
                                        data=json.dumps(dict()),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 400)

    def test_invalid_addlink_emptynameaddr(self):
        with self.client:
            self.login()
            response = self.client.post('/addlink',
                                        data=json.dumps(
                                            dict(name='', address='')),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 400)
            lnk = dblink.query.filter(dblink.name == '').first()
            self.assertIsNone(lnk)

    def test_addlink_samename(self):
        with self.client:
            self.login()
            # Add a new link first
            lnk = dblink('newlink', 'http://newlink.com', 0)
            db.session.add(lnk)
            db.session.commit()
            response = self.client.post('/addlink',
                                        data=json.dumps(
                                            dict(name='newlink',
                                                 address='http://link.com')),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            lnk = dblink.query.filter(
                dblink.address == 'http://link.com').first()
            self.assertIsNone(lnk)

    def test_addlink_sameaddress(self):
        with self.client:
            self.login()
            # Add a new link first
            lnk = dblink('newlink', 'http://newlink.com', 0)
            db.session.add(lnk)
            db.session.commit()
            response = self.client.post(
                '/addlink',
                data=json.dumps(dict(name='link',
                                     address='http://newlink.com')),
                content_type='application/json',
                follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            lnk = dblink.query.filter(dblink.name == 'link').first()
            self.assertIsNone(lnk)

    def test_editlink(self):
        with self.client:
            self.login()
            # Add a new link first
            lnk = dblink('editme', 'http://editme.com', 0)
            db.session.add(lnk)
            db.session.commit()
            response = self.client.post(
                '/editlink',
                data=json.dumps(
                    dict(id=1,
                         name='editedlink',
                         address='http://editedaddress.com')),
                content_type='application/json',
                follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            lnk = dblink.query.filter(dblink.linkid == 1).first()
            self.assertIsNotNone(lnk)
            self.assertEqual(lnk.name, 'editedlink')
            self.assertEqual(lnk.address, 'http://editedaddress.com')

    def test_invalid_editlink_noid(self):
        with self.client:
            self.login()
            # Add a new link first
            lnk = dblink('editme', 'http://editaddress.com', 0)
            db.session.add(lnk)
            db.session.commit()
            response = self.client.post(
                '/editlink',
                data=json.dumps(
                    dict(name='editedlink',
                         address='http://editedaddress.com')),
                content_type='application/json',
                follow_redirects=True)
            self.assertEqual(response.status_code, 400)
            lnk = dblink.query.filter(dblink.linkid == 1).first()
            self.assertIsNotNone(lnk)
            self.assertEqual(lnk.name, 'editme')
            self.assertEqual(lnk.address, 'http://editaddress.com')

    def test_invalid_editlink_id(self):
        with self.client:
            self.login()
            # Add a new link first
            lnk = dblink('editme', 'http://editaddress.com', 0)
            db.session.add(lnk)
            db.session.commit()
            response = self.client.post(
                '/editlink',
                data=json.dumps(
                    dict(id=10,
                         name='editedlink',
                         address='http://editedaddress.com')),
                content_type='application/json',
                follow_redirects=True)
            self.assertEqual(response.status_code, 400)
            lnk = dblink.query.filter(dblink.linkid == 1).first()
            self.assertIsNotNone(lnk)
            self.assertEqual(lnk.name, 'editme')
            self.assertEqual(lnk.address, 'http://editaddress.com')

    def test_invalid_editlink_nameaddr(self):
        with self.client:
            self.login()
            # Add a new link first
            lnk = dblink('editme', 'http://editaddress.com', 0)
            db.session.add(lnk)
            db.session.commit()
            response = self.client.post('/editlink',
                                        data=json.dumps(
                                            dict(id=1, name='', address='')),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 400)
            lnk = dblink.query.filter(dblink.linkid == 1).first()
            self.assertIsNotNone(lnk)
            self.assertEqual(lnk.name, 'editme')
            self.assertEqual(lnk.address, 'http://editaddress.com')

    def test_editlink_nochange(self):
        with self.client:
            self.login()
            # Add a new link first
            lnk = dblink('editme', 'http://editme.com', 0)
            db.session.add(lnk)
            db.session.commit()
            response = self.client.post('/editlink',
                                        data=json.dumps(
                                            dict(id=1,
                                                 name='editme',
                                                 address='http://editme.com')),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            lnk = dblink.query.filter(dblink.linkid == 1).first()
            self.assertIsNotNone(lnk)
            self.assertEqual(lnk.name, 'editme')
            self.assertEqual(lnk.address, 'http://editme.com')

    def test_editlink_samename(self):
        with self.client:
            self.login()
            # Add two new links first
            lnk = dblink('editme1', 'http://editme1.com', 0)
            db.session.add(lnk)
            db.session.commit()
            lnk = dblink('editme2', 'http://editme2.com', 0)
            db.session.add(lnk)
            db.session.commit()
            response = self.client.post('/editlink',
                                        data=json.dumps(
                                            dict(id=1,
                                                 name='editme2',
                                                 address='http://editme.com')),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            lnk = dblink.query.filter(dblink.linkid == 1).first()
            self.assertIsNotNone(lnk)
            self.assertEqual(lnk.name, 'editme1')
            self.assertEqual(lnk.address, 'http://editme1.com')

    def test_editlink_sameaddr(self):
        with self.client:
            self.login()
            # Add two new links first
            lnk = dblink('editme1', 'http://editme1.com', 0)
            db.session.add(lnk)
            db.session.commit()
            lnk = dblink('editme2', 'http://editme2.com', 0)
            db.session.add(lnk)
            db.session.commit()
            response = self.client.post('/editlink',
                                        data=json.dumps(
                                            dict(
                                                id=1,
                                                name='editme1',
                                                address='http://editme2.com')),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            lnk = dblink.query.filter(dblink.linkid == 1).first()
            self.assertIsNotNone(lnk)
            self.assertEqual(lnk.name, 'editme1')
            self.assertEqual(lnk.address, 'http://editme1.com')

    def test_removelink(self):
        with self.client:
            self.login()
            # Add a new link first
            lnk = dblink('removeme', 'http://removeme.com', 0)
            db.session.add(lnk)
            db.session.commit()
            response = self.client.post('/removelink',
                                        data=json.dumps(dict(id=1)),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            lnk = dblink.query.filter(dblink.name == 'removeme').first()
            self.assertIsNone(lnk)

    def test_invalid_removelink_noid(self):
        with self.client:
            self.login()
            # Add a new link first
            lnk = dblink('removeme', 'http://removeme.com', 0)
            db.session.add(lnk)
            db.session.commit()
            response = self.client.post('/removelink',
                                        data=json.dumps(dict()),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 400)
            lnk = dblink.query.filter(dblink.name == 'removeme').first()
            self.assertIsNotNone(lnk)

    def test_invalid_removelink_id(self):
        with self.client:
            self.login()
            # Add a new link first
            lnk = dblink('removeme', 'http://removeme.com', 0)
            db.session.add(lnk)
            db.session.commit()
            response = self.client.post('/removelink',
                                        data=json.dumps(dict(id=10)),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 400)
            lnk = dblink.query.filter(dblink.name == 'removeme').first()
            self.assertIsNotNone(lnk)

    # TODO: Add more tests!


if __name__ == "__main__":
    unittest.main()
