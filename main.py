#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        self.response.out.write(t.render(params))

    def render (self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    subject = db.StringProperty(required = True)
    blog = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

#class MainPage(Handler):
#    def get(self):
#        self.response.write('<a href="/blog">blog</a>')

class BlogFrontHandler(Handler):
    def blog_front(self, subject="", content=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        self.render_str("blogfront.html", blogs=blogs)

    def get(self):
        self.blog_front("", "")


class NewPostHandler(Handler):
    def get(self, subject='', content='', error=''):
        self.render('newpost.html', content=content, subject=subject, error=error)

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            b = Blog(subject = subject, blog=content)
            b.put()
            self.redirect("/blog/" + str(b.key().id()) + '/')
        else:
            error = "We need both a subject and some content!"
            self.render('newpost.html', subject=subject, content=content, error=error)

class PermalinkHandler(Handler):
    def get(self, post_id):
        b = Blog.get_by_id(int(post_id))
        self.render('display.html', blog = b)



app = webapp2.WSGIApplication([
("/", BlogFrontHandler), ('/blog/newpost/', NewPostHandler), webapp2.Route('/blog/<post_id:\d+>/', handler=PermalinkHandler) ,
], debug=True)
