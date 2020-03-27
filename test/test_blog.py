
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

    def test_invalid_newcategory_noname(self):
        with self.client:
            self.login()
            response = self.client.post('/newcategory',
                                        data=json.dumps(dict()),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 400)
            cat = dbcategory.query.filter(dbcategory.catid == 1).first()
            self.assertIsNone(cat)

    def test_invalid_newcategory_emptyname(self):
        with self.client:
            self.login()
            response = self.client.post('/newcategory',
                                        data=json.dumps(dict(name='')),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 400)
            cat = dbcategory.query.filter(dbcategory.catid == 1).first()
            self.assertIsNone(cat)

    def test_newcategory_samename(self):
        with self.client:
            self.login()
            category = dbcategory('anothercategory', 0)
            db.session.add(category)
            db.session.commit()
            response = self.client.post('/newcategory',
                                        data=json.dumps(
                                            dict(name='anothercategory')),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            cat = dbcategory.query.filter(dbcategory.catid == 2).first()
            self.assertIsNone(cat)

    def test_editcategory(self):
        with self.client:
            self.login()
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

    def test_invalid_editcategory_noidname(self):
        with self.client:
            self.login()
            category = dbcategory('Other', 0)
            db.session.add(category)
            db.session.commit()
            response = self.client.post('/editcategory',
                                        data=json.dumps(dict()),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 400)
            cat = dbcategory.query.filter(dbcategory.catid == 1).first()
            self.assertIsNotNone(cat)
            self.assertEqual(cat.name, 'Other')

    def test_invalid_editcategory_id(self):
        with self.client:
            self.login()
            category = dbcategory('Other', 0)
            db.session.add(category)
            db.session.commit()
            response = self.client.post('/editcategory',
                                        data=json.dumps(
                                            dict(id=100, name='Test')),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 400)
            cat = dbcategory.query.filter(dbcategory.catid == 1).first()
            self.assertIsNotNone(cat)
            self.assertEqual(cat.name, 'Other')

    def test_invalid_editcategory_emptyname(self):
        with self.client:
            self.login()
            category = dbcategory('Other', 0)
            db.session.add(category)
            db.session.commit()
            response = self.client.post('/editcategory',
                                        data=json.dumps(dict(id=1, name='')),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 400)
            cat = dbcategory.query.filter(dbcategory.catid == 1).first()
            self.assertIsNotNone(cat)
            self.assertEqual(cat.name, 'Other')

    def test_editcategory_samename(self):
        with self.client:
            self.login()
            category = dbcategory('Other', 0)
            db.session.add(category)
            db.session.commit()
            response = self.client.post('/editcategory',
                                        data=json.dumps(
                                            dict(id=1, name='Other')),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            cat = dbcategory.query.filter(dbcategory.catid == 1).first()
            self.assertIsNotNone(cat)
            self.assertEqual(cat.name, 'Other')

    def test_editcategory_existingname(self):
        with self.client:
            self.login()
            category = dbcategory('Other1', 0)
            db.session.add(category)
            category = dbcategory('Other2', 0)
            db.session.add(category)
            db.session.commit()
            response = self.client.post('/editcategory',
                                        data=json.dumps(
                                            dict(id=2, name='Other1')),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            cat = dbcategory.query.filter(dbcategory.catid == 2).first()
            self.assertIsNotNone(cat)
            self.assertEqual(cat.name, 'Other2')

    def test_removecategory_nopost(self):
        with self.client:
            self.login()
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
            category = dbcategory('removeme', 0)
            db.session.add(category)
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

    def test_share(self):
        with self.client:
            self.login()
            category = dbcategory('Other', 0)
            db.session.add(category)
            post = dbpost(
                'testtitle', 'testcontent',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 1,
                '', 0)
            db.session.add(post)
            db.session.commit()
            response = self.client.get('/share?postid=1',
                                       follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'testtitle', response.data)
            self.assertIn(b'testcontent', response.data)

    def test_invalid_share_noid(self):
        with self.client:
            self.login()
            category = dbcategory('Other', 0)
            db.session.add(category)
            post = dbpost(
                'testtitle', 'testcontent',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 1,
                '', 0)
            db.session.add(post)
            db.session.commit()
            response = self.client.get('/share', follow_redirects=False)
            self.assertEqual(response.status_code, 400)

    def test_invalid_share_id(self):
        with self.client:
            self.login()
            category = dbcategory('Other', 0)
            db.session.add(category)
            post = dbpost(
                'testtitle', 'testcontent',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 1,
                '', 0)
            db.session.add(post)
            db.session.commit()
            response = self.client.get('/share?postid=100',
                                       follow_redirects=False)
            self.assertEqual(response.status_code, 400)

    def test_post_page_get_noid(self):
        with self.client:
            self.login()
            response = self.client.get('/post', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

    def test_post_page_get_id(self):
        with self.client:
            self.login()
            category = dbcategory('Other', 0)
            db.session.add(category)
            post = dbpost(
                'testtitle', 'testcontent',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 1,
                'http://testaddr.com', 0)
            db.session.add(post)
            db.session.commit()
            response = self.client.get('/post?id=1', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'testtitle', response.data)
            self.assertIn(b'testcontent', response.data)
            self.assertIn(b'http://testaddr.com', response.data)

    def test_post_page_post_noid(self):
        with self.client:
            self.login()
            hashtag = dbtag('test', 1, 0)
            db.session.add(hashtag)
            db.session.commit()
            response = self.client.post('/post',
                                        data=dict(
                                            category='1',
                                            disablecomments='No',
                                            pinned='No',
                                            title='testtitle',
                                            mediaaddr='http://testaddr.com',
                                            content='testcontent #test #post',
                                            postid=''),
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            post = dbpost.query.filter(dbpost.postid == 1).first()
            self.assertIsNotNone(post)
            self.assertEqual(post.category, 1)
            self.assertEqual(post.flags, 0)
            self.assertEqual(post.title, 'testtitle')
            self.assertEqual(post.mediaaddr, 'http://testaddr.com')
            self.assertEqual(post.content, 'testcontent #test #post')
            hashtag1 = dbtag.query.filter(dbtag.keyword == 'test').first()
            self.assertEqual(hashtag1.frequency, 2)
            hashtag2 = dbtag.query.filter(dbtag.keyword == 'post').first()
            self.assertEqual(hashtag2.frequency, 1)

    def test_post_page_post_id(self):
        with self.client:
            self.login()
            category = dbcategory('Test1', 0)
            db.session.add(category)
            category = dbcategory('Test2', 0)
            db.session.add(category)
            hashtag = dbtag('test', 2, 0)
            db.session.add(hashtag)
            post = dbpost(
                'testtitle', 'testcontent #test #post1',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 1,
                'http://testaddr.com', 0)
            db.session.add(post)
            db.session.commit()
            response = self.client.post(
                '/post',
                data=dict(category='2',
                          disablecomments='No',
                          pinned='No',
                          title='testtitle2',
                          mediaaddr='http://testaddr2.com',
                          content='testcontent2 #test #post2',
                          postid='1'),
                follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            post = dbpost.query.filter(dbpost.postid == 1).first()
            self.assertIsNotNone(post)
            self.assertEqual(post.category, 2)
            self.assertEqual(post.flags, 0)
            self.assertEqual(post.title, 'testtitle2')
            self.assertEqual(post.mediaaddr, 'http://testaddr2.com')
            self.assertEqual(post.content, 'testcontent2 #test #post2')
            hashtag1 = dbtag.query.filter(dbtag.keyword == 'test').first()
            self.assertEqual(hashtag1.frequency, 2)
            hashtag2 = dbtag.query.filter(dbtag.keyword == 'post2').first()
            self.assertEqual(hashtag2.frequency, 1)
            hashtag3 = dbtag.query.filter(dbtag.keyword == 'post1').first()
            self.assertIsNone(hashtag3)

    def test_invalid_post_page_post_noid(self):
        with self.client:
            self.login()
            response = self.client.post('/post',
                                        data=dict(category='',
                                                  disablecomments='',
                                                  pinned='',
                                                  title='',
                                                  mediaaddr='',
                                                  content='',
                                                  postid=''),
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            post = dbpost.query.filter(dbpost.postid == 1).first()
            self.assertIsNone(post)

    def test_deletepost(self):
        with self.client:
            self.login()
            hashtag = dbtag('test', 2, 0)
            db.session.add(hashtag)
            hashtag = dbtag('post', 1, 0)
            db.session.add(hashtag)
            post = dbpost(
                'testtitle', 'testcontent #test #post',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 1,
                'http://testaddr.com', 0)
            db.session.add(post)
            db.session.commit()
            response = self.client.post('/deletepost',
                                        data=json.dumps(dict(id=1)),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            post = dbpost.query.filter(dbpost.postid == 1).first()
            self.assertIsNone(post)
            hashtag1 = dbtag.query.filter(dbtag.keyword == 'test').first()
            self.assertEqual(hashtag1.frequency, 1)
            hashtag2 = dbtag.query.filter(dbtag.keyword == 'post').first()
            self.assertIsNone(hashtag2)

    def test_invalid_deletepost_noid(self):
        with self.client:
            self.login()
            hashtag = dbtag('test', 1, 0)
            db.session.add(hashtag)
            post = dbpost(
                'testtitle', 'testcontent #test #post',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 1,
                'http://testaddr.com', 0)
            db.session.add(post)
            db.session.commit()
            response = self.client.post('/deletepost',
                                        data=json.dumps(dict()),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 400)
            post = dbpost.query.filter(dbpost.postid == 1).first()
            self.assertIsNotNone(post)
            hashtag1 = dbtag.query.filter(dbtag.keyword == 'test').first()
            self.assertEqual(hashtag1.frequency, 1)

    def test_invalid_deletepost_id(self):
        with self.client:
            self.login()
            hashtag = dbtag('test', 1, 0)
            db.session.add(hashtag)
            post = dbpost(
                'testtitle', 'testcontent #test #post',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 1,
                'http://testaddr.com', 0)
            db.session.add(post)
            db.session.commit()
            response = self.client.post('/deletepost',
                                        data=json.dumps(dict(id=10)),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 400)
            post = dbpost.query.filter(dbpost.postid == 1).first()
            self.assertIsNotNone(post)
            hashtag1 = dbtag.query.filter(dbtag.keyword == 'test').first()
            self.assertEqual(hashtag1.frequency, 1)

    def test_404_page(self):
        with self.client:
            response = self.client.get('/page_not_found',
                                       follow_redirects=True)
            self.assertEqual(response.status_code, 404)
            self.assertIn(b'404', response.data)

    def test_403_page(self):
        with self.client:
            response = self.client.get('/post', follow_redirects=True)
            self.assertEqual(response.status_code, 403)
            self.assertIn(b'403', response.data)

    def test_400_page(self):
        with self.client:
            self.login()
            response = self.client.get('/share?postid=a',
                                       follow_redirects=True)
            self.assertEqual(response.status_code, 400)
            self.assertIn(b'400', response.data)

    def test_deletecomment(self):
        with self.client:
            self.login()
            post = dbpost(
                'testtitle', 'testcontent #test #post',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1, 1,
                'http://testaddr.com', 0)
            db.session.add(post)
            comment = dbcomment(
                1, 'testcomment',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'dearuser', '', '', 0)
            db.session.add(comment)
            db.session.commit()
            response = self.client.post('/deletecomment',
                                        data=json.dumps(dict(id=1)),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            comment = dbcomment.query.filter(dbcomment.cmtid == 1).first()
            self.assertIsNone(comment)

    def test_invalid_deletecomment_noid(self):
        with self.client:
            self.login()
            post = dbpost(
                'testtitle', 'testcontent #test #post',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1, 1,
                'http://testaddr.com', 0)
            db.session.add(post)
            comment = dbcomment(
                1, 'testcomment',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'dearuser', '', '', 0)
            db.session.add(comment)
            db.session.commit()
            response = self.client.post('/deletecomment',
                                        data=json.dumps(dict()),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 400)
            comment = dbcomment.query.filter(dbcomment.cmtid == 1).first()
            self.assertIsNotNone(comment)

    def test_invalid_deletecomment_id(self):
        with self.client:
            self.login()
            post = dbpost(
                'testtitle', 'testcontent #test #post',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1, 1,
                'http://testaddr.com', 0)
            db.session.add(post)
            comment = dbcomment(
                1, 'testcomment',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'dearuser', '', '', 0)
            db.session.add(comment)
            db.session.commit()
            response = self.client.post('/deletecomment',
                                        data=json.dumps(dict(id=10)),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 400)
            comment = dbcomment.query.filter(dbcomment.cmtid == 1).first()
            self.assertIsNotNone(comment)

    def test_formatdate(self):
        dt = datetime.datetime.now()
        strdt = dt.strftime('%Y-%m-%d %H:%M:%S')
        config = install()
        config['calendar'] = 'Gregorian'
        saveConfig(config)
        newdt = formatDateTime(strdt, '%Y-%m-%d %H:%M:%S')
        self.assertEqual(newdt, strdt.lstrip('0') \
            .replace(' 0', ' ').replace(':0', ':').replace('-0', '-'))
        config['calendar'] = 'Jalali'
        saveConfig(config)
        newdt = formatDateTime(strdt, '%Y-%m-%d')
        jdt = jdatetime.GregorianToJalali(dt.year, dt.month, dt.day)
        strdt = str(jdt.jyear) + '-' + str(jdt.jmonth) + '-' + str(jdt.jday)
        self.assertEqual(newdt, strdt)

    def test_getconfig(self):
        config = getConfig()
        newconfig = install()
        self.assertEqual(config, newconfig)

    def test_hashtag_search(self):
        with self.client:
            tag = dbtag('test', 1, 1)
            db.session.add(tag)
            db.session.commit()
            response = self.client.get('/?tag=test', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            tag = dbtag.query.filter(dbtag.keyword == 'test').first()
            self.assertIsNotNone(tag)
            self.assertEqual(tag.popularity, 2)

    def test_approvecomment(self):
        with self.client:
            self.login()
            comment = dbcomment(
                0, 'testcontent',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'test',
                '', '', 0)
            db.session.add(comment)
            db.session.commit()
            response = self.client.post('/approvecomment',
                                        data=json.dumps(dict(id=1)),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            comment = dbcomment.query.filter(dbcomment.cmtid == 1).first()
            self.assertIsNotNone(comment)
            self.assertEqual(comment.status, 3)

    def test_invalid_approvecomment_noid(self):
        with self.client:
            self.login()
            comment = dbcomment(
                0, 'testcontent',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'test',
                '', '', 0)
            db.session.add(comment)
            db.session.commit()
            response = self.client.post('/approvecomment',
                                        data=json.dumps(dict()),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 400)
            comment = dbcomment.query.filter(dbcomment.cmtid == 1).first()
            self.assertIsNotNone(comment)
            self.assertEqual(comment.status, 0)

    def test_invalid_approvecomment_id(self):
        with self.client:
            self.login()
            comment = dbcomment(
                0, 'testcontent',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'test',
                '', '', 0)
            db.session.add(comment)
            db.session.commit()
            response = self.client.post('/approvecomment',
                                        data=json.dumps(dict(id=10)),
                                        content_type='application/json',
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 400)
            comment = dbcomment.query.filter(dbcomment.cmtid == 1).first()
            self.assertIsNotNone(comment)
            self.assertEqual(comment.status, 0)

    def test_commentmoderation(self):
        with self.client:
            self.login()
            comment = dbcomment(
                0, 'testcontent',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'test',
                '', '', 0)
            db.session.add(comment)
            db.session.commit()
            response = self.client.get('/commentmoderation',
                                       follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'testcontent', response.data)

    def test_comments(self):
        with self.client:
            self.login()
            post = dbpost(
                'testtitle', 'test #content',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 0,
                '', 0)
            db.session.add(post)
            comment = dbcomment(
                1, 'testcomment',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'test',
                '', '', 0)
            db.session.add(comment)
            db.session.commit()
            response = self.client.get('/comments?postid=1',
                                       follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            comment = dbcomment.query.filter(dbcomment.cmtid == 1).first()
            self.assertEqual(comment.status, 1)
            self.assertIn(b'testcomment', response.data)

    def test_invalid_comments_id(self):
        with self.client:
            response = self.client.get('/comments?postid=10',
                                       follow_redirects=True)
            self.assertEqual(response.status_code, 400)

    def test_comments_user(self):
        with self.client:
            post = dbpost(
                'testtitle', 'test #content',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 0,
                '', 0)
            db.session.add(post)
            comment = dbcomment(
                1, 'testcomment1',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'test',
                '', '', 0)
            db.session.add(comment)
            comment = dbcomment(
                1, 'testcomment2',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'test2',
                '', '', 2)
            db.session.add(comment)
            db.session.commit()
            response = self.client.get('/comments?postid=1',
                                       follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            comment = dbcomment.query.filter(dbcomment.cmtid == 1).first()
            self.assertEqual(comment.status, 0)
            self.assertNotIn(b'testcomment1', response.data)
            comment = dbcomment.query.filter(dbcomment.cmtid == 2).first()
            self.assertEqual(comment.status, 2)
            self.assertIn(b'testcomment2', response.data)

    def test_comments_post(self):
        with self.client:
            post = dbpost(
                'testtitle', 'testcontent',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 0,
                '', 0)
            db.session.add(post)
            db.session.commit()
            config = install()
            config['disablecomments'] = 'No'
            saveConfig(config)
            response = self.client.post('/comments?postid=1',
                                        data=dict(postid=1,
                                                  name='testname',
                                                  mailaddr='test@test.com',
                                                  website='http://test.com',
                                                  content='testcomment'),
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            comment = dbcomment.query.filter(dbcomment.cmtid == 1).first()
            self.assertIsNotNone(comment)
            self.assertEqual(comment.pid, 1)
            self.assertEqual(comment.name, 'testname')
            self.assertEqual(comment.emailaddr, 'test@test.com')
            self.assertEqual(comment.website, 'http://test.com')
            self.assertEqual(comment.content, 'testcomment')
            self.assertEqual(comment.status, 0)

    def test_comments_post_disabled(self):
        with self.client:
            self.login()
            post = dbpost(
                'testtitle', 'testcontent',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 0,
                '', 0)
            db.session.add(post)
            db.session.commit()
            config = install()
            config['disablecomments'] = 'Yes'
            saveConfig(config)
            response = self.client.post('/comments?postid=1',
                                        data=dict(postid=1,
                                                  name='testname',
                                                  mailaddr='test@test.com',
                                                  website='http://test.com',
                                                  content='testcomment'),
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            comment = dbcomment.query.filter(dbcomment.cmtid == 1).first()
            self.assertIsNone(comment)

    def test_invalid_comments_post(self):
        with self.client:
            self.login()
            post = dbpost(
                'testtitle', 'testcontent',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 0,
                '', 0)
            db.session.add(post)
            db.session.commit()
            response = self.client.post('/comments?postid=1',
                                        data=dict(postid=1,
                                                  name='',
                                                  mailaddr='test',
                                                  website='test',
                                                  content=''),
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            comment = dbcomment.query.filter(dbcomment.cmtid == 1).first()
            self.assertIsNone(comment)
            self.assertNotIn(b'testcomment', response.data)

    def test_prcText(self):
        ret = prcText('hello #dear user!', 'https://www.site.com/blog')
        text = "hello <a href='https://www.site.com/blog/?tag=dear'" + \
             " class='hashtag'>#dear</a> user!"
        self.assertEqual(ret, Markup(text))

    def test_config_get(self):
        with self.client:
            self.login()
            response = self.client.get('/config', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

    def test_config_post(self):
        with self.client:
            self.login()
            response = self.client.post('/config',
                                        data=dict(title='testtitle',
                                                  desc='testdesc',
                                                  currpwd='admin',
                                                  newpwd='',
                                                  confirmpwd='',
                                                  dispname='testname',
                                                  mailaddr='test@test.com',
                                                  ppp=16,
                                                  dtformat='%N',
                                                  calendar='Gregorian',
                                                  autoapproval='Yes',
                                                  disablecomments='Yes'),
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            config = getConfig()
            pwd = hashlib.md5('admin'.encode('utf-8')).hexdigest()
            self.assertEqual(config['title'], 'testtitle')
            self.assertEqual(config['desc'], 'testdesc')
            self.assertEqual(config['pwd'], pwd)
            self.assertEqual(config['dispname'], 'testname')
            self.assertEqual(config['mailaddr'], 'test@test.com')
            self.assertEqual(config['ppp'], 16)
            self.assertEqual(config['dtformat'], '%N')
            self.assertEqual(config['calendar'], 'Gregorian')
            self.assertEqual(config['autoapproval'], 'Yes')
            self.assertEqual(config['disablecomments'], 'Yes')

    def test_config_post_newpwd(self):
        with self.client:
            self.login()
            response = self.client.post('/config',
                                        data=dict(title='testtitle',
                                                  desc='testdesc',
                                                  currpwd='admin',
                                                  newpwd='1234567890',
                                                  confirmpwd='1234567890',
                                                  dispname='testname',
                                                  mailaddr='test@test.com',
                                                  ppp=16,
                                                  dtformat='%N',
                                                  calendar='Gregorian',
                                                  autoapproval='Yes',
                                                  disablecomments='Yes'),
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            config = getConfig()
            pwd = hashlib.md5('1234567890'.encode('utf-8')).hexdigest()
            self.assertEqual(config['title'], 'testtitle')
            self.assertEqual(config['desc'], 'testdesc')
            self.assertEqual(config['pwd'], pwd)
            self.assertEqual(config['dispname'], 'testname')
            self.assertEqual(config['mailaddr'], 'test@test.com')
            self.assertEqual(config['ppp'], 16)
            self.assertEqual(config['dtformat'], '%N')
            self.assertEqual(config['calendar'], 'Gregorian')
            self.assertEqual(config['autoapproval'], 'Yes')
            self.assertEqual(config['disablecomments'], 'Yes')

    def test_invalid_config_post(self):
        with self.client:
            self.login()
            response = self.client.post('/config',
                                        data=dict(title='',
                                                  desc='',
                                                  currpwd='admin',
                                                  newpwd='1234',
                                                  confirmpwd='12345',
                                                  dispname='',
                                                  mailaddr='testmail',
                                                  dtformat='',
                                                  calendar='Gregorian',
                                                  autoapproval='Yes',
                                                  disablecomments='Yes'),
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'testmail', response.data)

    def test_config_post_wrongpwd(self):
        with self.client:
            self.login()
            response = self.client.post('/config',
                                        data=dict(title='testtitle',
                                                  desc='testdesc',
                                                  currpwd='12345',
                                                  newpwd='',
                                                  confirmpwd='',
                                                  dispname='testname',
                                                  mailaddr='testmail@test.com',
                                                  ppp=16,
                                                  dtformat='%N',
                                                  calendar='Gregorian',
                                                  autoapproval='Yes',
                                                  disablecomments='Yes'),
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 401)
            config = getConfig()
            pwd = hashlib.md5('admin'.encode('utf-8')).hexdigest()
            self.assertEqual(config['pwd'], pwd)
            self.assertNotEqual(config['title'], 'testtitle')
            self.assertNotEqual(config['desc'], 'testdesc')
            self.assertNotEqual(config['dispname'], 'testname')
            self.assertNotEqual(config['mailaddr'], 'testmail@test.com')
            self.assertNotEqual(config['ppp'], 16)
            self.assertNotEqual(config['dtformat'], '%N')
            self.assertNotEqual(config['calendar'], 'Gregorian')
            self.assertNotEqual(config['autoapproval'], 'Yes')
            self.assertNotEqual(config['disablecomments'], 'Yes')

    def test_show(self):
        with self.client:
            self.login()
            category = dbcategory('Other', 0)
            db.session.add(category)
            post = dbpost(
                'testtitle', 'testcontent',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1, 1,
                '', 0)
            db.session.add(post)
            comment = dbcomment(
                1, 'testcomment',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'testname', '', '', 0)
            db.session.add(comment)
            db.session.commit()
            response = self.client.get('/show?id=1', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'testtitle', response.data)
            self.assertIn(b'testcontent', response.data)
            self.assertIn(b'testname', response.data)
            self.assertIn(b'testcomment', response.data)

    def test_show_user(self):
        with self.client:
            category = dbcategory('Other', 0)
            db.session.add(category)
            post = dbpost(
                'testtitle', 'testcontent',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1, 1,
                '', 0)
            db.session.add(post)
            comment = dbcomment(
                1, 'testcomment',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'testname', '', '', 3)
            db.session.add(comment)
            db.session.commit()
            response = self.client.get('/show?id=1', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'testtitle', response.data)
            self.assertIn(b'testcontent', response.data)
            self.assertIn(b'testname', response.data)
            self.assertIn(b'testcomment', response.data)

    def test_invalid_show_id(self):
        with self.client:
            response = self.client.get('/show?id=100', follow_redirects=True)
            self.assertEqual(response.status_code, 400)

    def test_page_get(self):
        with self.client:
            self.login()
            category = dbcategory('Other', 0)
            db.session.add(category)
            post = dbpost(
                'testtitle1', 'testcontent1 #test',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 1,
                '', 0)
            db.session.add(post)
            post = dbpost(
                'testtitle2', 'testcontent2 #test' * 128,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 1,
                '', 0)
            db.session.add(post)
            db.session.commit()
            response = self.client.get(
                '/page?page=0&search=test&tag=test&category=1',
                follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'testcontent1', response.data)
            self.assertIn(b'testcontent2', response.data)
            self.assertIn(b'...', response.data)

    def test_page_sort(self):
        with self.client:
            self.login()
            config = getConfig()
            config['ppp'] = 1
            saveConfig(config)
            category = dbcategory('Other', 0)
            db.session.add(category)
            post = dbpost(
                'testtitle1', 'testcontent1 #test',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1, 1,
                '', 0)
            db.session.add(post)
            post = dbpost(
                'testtitle2', 'testcontent2 #test' * 128,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 1,
                '', 0)
            db.session.add(post)
            db.session.commit()
            response = self.client.get('/page?page=0&sort=ascdate',
                                       follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'testcontent1', response.data)
            self.assertNotIn(b'testcontent2', response.data)
            response = self.client.get('/page?page=0&sort=descdate',
                                       follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'testcontent2', response.data)
            self.assertNotIn(b'testcontent1', response.data)
            response = self.client.get('/page?page=0&sort=asccomments',
                                       follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'testcontent2', response.data)
            self.assertNotIn(b'testcontent1', response.data)
            response = self.client.get('/page?page=0&sort=desccomments',
                                       follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'testcontent1', response.data)
            self.assertNotIn(b'testcontent2', response.data)

    def test_page_ppp(self):
        with self.client:
            config = getConfig()
            config['ppp'] = 1
            saveConfig(config)
            category = dbcategory('Other', 0)
            db.session.add(category)
            post = dbpost(
                'testtitle1', 'testcontent1 #test',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 1,
                '', 0)
            db.session.add(post)
            post = dbpost(
                'testtitle2', 'testcontent2 #test' * 128,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 1,
                '', 0)
            db.session.add(post)
            db.session.commit()
            response = self.client.get('/page?page=0&sort=ascdate',
                                       follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'testcontent1', response.data)
            self.assertNotIn(b'testcontent2', response.data)
            response = self.client.get('/page?page=1&sort=ascdate',
                                       follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'testcontent2', response.data)
            self.assertNotIn(b'testcontent1', response.data)

    def test_page_end(self):
        with self.client:
            category = dbcategory('Other', 0)
            db.session.add(category)
            post = dbpost(
                'testtitle1', 'testcontent1 #test',
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 1,
                '', 0)
            db.session.add(post)
            post = dbpost(
                'testtitle2', 'testcontent2 #test' * 128,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 1,
                '', 0)
            db.session.add(post)
            db.session.commit()
            response = self.client.get('/page?page=10', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'END.', response.data)

    # TODO: Add more tests!


if __name__ == "__main__":
    unittest.main()
