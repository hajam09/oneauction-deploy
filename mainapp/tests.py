from django.test import TestCase, Client
from mainapp.models import CustomerProfile, Item
from django.contrib.auth.models import User
from datetime import datetime
from django.urls import path, include, reverse, resolve
from mainapp.models import CustomerProfile, Item
from mainapp.views import index, login, signup, log_out, new_item, closedauction, update_profile, itempage, user_biddings
import json

class CustomerProfileTestCase(TestCase):
	###############Test_Models##########################

	def create_user(self, u, p, f, l):
		return User.objects.create_user(username=u, password=p, first_name=f, last_name=l)

	def create_user_profile(self, u ,b, e):
		return u.customerprofile_set.create(birthDate=b, email=e)

	def create_item(self, s, t, d, e, i, iu, p, b, st):
		return Item.objects.create(seller=s, title=t,
			description=d, expiredate=e,
			imagename=i, imageurl=iu,
			price=p, buyer=b, status=st)

	def test_create_user(self):
		newuser = self.create_user("oliver.queen@yahoo.com", "RanDomPasWord", "Oliver", "Queen")
		newprofile = self.create_user_profile(newuser, "2019-03-22", "oliver.queen@yahoo.com")
		self.assertTrue(isinstance(newuser, User))
		self.assertTrue(isinstance(newprofile, CustomerProfile))

	def test_user_attributes(self):
		newuser =self.create_user("barry.allen@yahoo.com", "RanDoasdPasWord", "Barry", "Allen")
		newprofile = self.create_user_profile(newuser, "2019-01-11", "barry.allen@yahoo.com")
		self.assertEqual(newuser.username, "barry.allen@yahoo.com")
		self.assertEqual(newuser.first_name, "Barry")
		self.assertEqual(newuser.last_name, "Allen")

	def test_profile_attribute(self):
		newuser =self.create_user("cisco.ramone@gmail.com", "Qgui4U3", "Cisco", "Ramone")
		newprofile = self.create_user_profile(newuser, "1995-07-12", "cisco.ramone@gmail.com")
		self.assertEqual(newprofile.birthDate, "1995-07-12")
		self.assertEqual(newprofile.email, "cisco.ramone@gmail.com")

	def test_create_item(self):
		seller = self.create_user("caitlin.snow@yahoo.com", "fgert5t4gt", "Caitlin", "Snow")
		sellerprofile = self.create_user_profile(seller, "1989-05-16", "caitlin.snow@yahoo.com")

		title = "Water Bottle"
		description = "Whether you're commuting, hiking or at the gym, a reusable water bottle is a handy way of ensuring you get enough water throughout the day while not wasting any plastic."
		expiredate = "2020-01-01"
		imagename = "waterbottle.jpg"
		imageurl = "/media/skyrim.jpg"
		price = 1.99
		status = False

		title2 = "Amazon Echo Dot 3rd Generation Smart speaker"
		description2 = "Echo Dot is a hands-free, voice-controlled device that uses the same far-field voice recognition as Amazon Echo. Dot has a small built-in speaker - it can also connect to your speakers over Bluetooth or with the included audio cable."
		expiredate2 = "2019-08-14"
		imagename2 = "echodot.jpg"
		imageurl2 = "/media/echodot.jpg"
		price2 = 22.99
		status2 = True

		buyer =self.create_user("joe.west@yahoo.com", "ghu47", "Joe", "West")
		buyerprofile = self.create_user_profile(buyer, "1999-11-18", "joe.west@yahoo.com")

		theitem = self.create_item(seller, title, description, expiredate, imagename, imageurl, price, buyer, status)
		self.assertTrue(isinstance(theitem, Item))

		theitem2 = self.create_item(seller, title2, description2, expiredate2, imagename2, imageurl2, price2, buyer, status2)
		self.assertTrue(isinstance(theitem2, Item))

	def test_item_attributes(self):
		seller = self.create_user("caitlin.snow@yahoo.com", "fgert5t4gt", "Caitlin", "Snow")
		sellerprofile = self.create_user_profile(seller, "1989-05-16", "caitlin.snow@yahoo.com")

		title = "Water Bottle"
		description = "Whether you're commuting, hiking or at the gym, a reusable water bottle is a handy way of ensuring you get enough water throughout the day while not wasting any plastic."
		expiredate = "2020-01-01"
		imagename = "waterbottle.jpg"
		imageurl = "/media/skyrim.jpg"
		price = 1.99
		status = False

		buyer =self.create_user("joe.west@yahoo.com", "ghu47", "Joe", "West")
		buyerprofile = self.create_user_profile(buyer, "1999-11-18", "joe.west@yahoo.com")

		theitem = self.create_item(seller, title, description, expiredate, imagename, imageurl, price, buyer, status)
		self.assertEqual(theitem.title, "Water Bottle")
		self.assertEqual(theitem.description,  "Whether you're commuting, hiking or at the gym, a reusable water bottle is a handy way of ensuring you get enough water throughout the day while not wasting any plastic.")
		self.assertEqual(theitem.expiredate, "2020-01-01")
		self.assertEqual(theitem.imageurl, "/media/skyrim.jpg")
		self.assertEqual(theitem.price, 1.99)
		self.assertEqual(theitem.status, False)

	###############Test_Models##########################


	###############Test_URLS##########################

	def test_urls(self):
		url = reverse('mainapp:index')
		self.assertEqual(resolve(url).func, index)
		self.assertEqual(resolve(url).url_name, "index")

		url = reverse('mainapp:login')
		self.assertEqual(resolve(url).func, login)
		self.assertEqual(resolve(url).url_name, "login")

		url = reverse('mainapp:signup')
		self.assertEqual(resolve(url).func, signup)
		self.assertEqual(resolve(url).url_name, "signup")

		url = reverse('mainapp:log_out')
		self.assertEqual(resolve(url).func, log_out)
		self.assertEqual(resolve(url).url_name, "log_out")

		url = reverse('mainapp:new_item')
		self.assertEqual(resolve(url).func, new_item)
		self.assertEqual(resolve(url).url_name, "new_item")

		url = reverse('mainapp:closedauction')
		self.assertEqual(resolve(url).func, closedauction)
		self.assertEqual(resolve(url).url_name, "closedauction")

		url = reverse('mainapp:update_profile')
		self.assertEqual(resolve(url).func, update_profile)
		self.assertEqual(resolve(url).url_name, "update_profile")

		url = reverse('mainapp:itempage')
		self.assertEqual(resolve(url).func, itempage)
		self.assertEqual(resolve(url).url_name, "itempage")

		url = reverse('mainapp:user_biddings')
		self.assertEqual(resolve(url).func, user_biddings)
		self.assertEqual(resolve(url).url_name, "user_biddings")

	###############Test_URLS##########################

	###############Test_Views##########################

	def test_URLS(self):
		client = Client()

		response = client.get(reverse('mainapp:index'))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'mainapp/frontpage.html')

		response = client.get(reverse('mainapp:login'))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'mainapp/login.html')

		# No templates are rendered in this function
		response = client.get(reverse('mainapp:log_out'))
		self.assertEqual(response.status_code, 302)
		# self.assertTemplateUsed(response, 'mainapp/frontpage.html')

		# No templates are rendered in this function
		response = client.get(reverse('mainapp:new_item'))
		self.assertEqual(response.status_code, 302)
		# self.assertTemplateUsed(response, 'mainapp/newitem.html')

		response = client.get(reverse('mainapp:closedauction'))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'mainapp/closedAuctions.html')

		# No templates are rendered in this function
		response = client.get(reverse('mainapp:update_profile'))
		self.assertEqual(response.status_code, 302)
		# self.assertTemplateUsed(response, 'mainapp/profilepage.html')

		response = client.get(reverse('mainapp:itempage'))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'mainapp/itempage.html')

		response = client.get(reverse('mainapp:user_biddings'))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'mainapp/userbiddings.html')

	###############Test_Views##########################