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
import webapp2
import os
import jinja2
import logging
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
    	t = jinja_env.get_template(template)
    	return t.render(params)

    def render(self, template, **kw):
    	self.write(self.render_str(template, **kw))


class Post(db.Model):
	title = db.StringProperty(required=True)
	body = db.TextProperty(required=True)
	created = db.DateTimeProperty(auto_now_add=True)


class MainPage(Handler):
	def get(self):
		self.redirect("/blog")

class NewPostForm(Handler):
	def render_front(self, title="", body="", error=""):
		self.render("form.html", title=title, body=body, error=error)

	def get(self):
		self.render_front()

	def post(self):
		title = self.request.get("title")
		body = self.request.get("body")

		if title and body:
			post = Post(title=title, body=body)
			post.put()

			self.redirect("/blog/" + str(post.key().id()))
		else:
			error = "We need both a title and body for the post."
			self.render_front(title, body, error)


class PostListing(Handler):
	def get_posts(self,limit,offset):
		offset = (int(offset) - 2) * int(limit)
		return db.GqlQuery("SELECT * FROM Post ORDER BY created DESC limit " + limit + " offset " + str(offset))

	def get(self):
		limit = 5
		page = self.request.get("page")

		if not page:
			self.redirect("/blog?page=1")
		else:
			page = int(page)
			page = page + 1
			page = str(page)
			self.render("allPosts.html", posts=self.get_posts(str(limit),page),page=page)

class ViewPost(Handler):
    def get(self, id):
    	post = Post.get_by_id(int(id))
    	if post == None:
    		error = "There is currently no post with an ID of " + id
    		self.render("errorpage.html",error=error)
    	else:
    		self.render("post.html", post=post)


routes = [
    ('/', MainPage),
    ('/blog', PostListing),
    ('/newpost', NewPostForm),
    webapp2.Route('/blog/<id:\d+>', ViewPost)
]

app = webapp2.WSGIApplication(routes, debug=True)
