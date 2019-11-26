from django.test import TestCase
from mainapp.models import CustomerProfile, Item
from django.contrib.auth.models import User
from datetime import datetime

class CustomerProfileTestCase(TestCase):
	def setUp(self):
		User.objects.create(username='user1')
		User.objects.create(username='user2')
		expiredate = str(datetime.now()).split(".")

		Item.objects.create(
			seller=User.objects.get(username='user1'),
			title="Game",
			description="Game-description",
			expiredate=expiredate[0],
			imagename="imagename",
			imageurl="imageurl",
			price=59.3,
			buyer=User.objects.get(username='user2'),
			status=False)

	def test_customer_profile(self):
		customerprofile = CustomerProfile.objects.get(title="Game")
		self.assertEqual(customerprofile.description, "Game-description")
		self.assertEqual(customerprofile.imagename, "imagename")
		self.assertEqual(customerprofile.price, 59.3)