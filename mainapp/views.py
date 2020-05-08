from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import HttpResponse, QueryDict, JsonResponse#, HttpResponseRedirect, Http404
# from django.template import RequestContext, loader
from django.contrib.sessions.models import Session
# from django.contrib.auth.hashers import make_password
# from django.db import IntegrityError
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import logout, authenticate, login as auth_login
# from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import CustomerAccountProfile, Book, Review, Category, Metrics
import string, random, csv, re, os, unidecode, time, requests#, ssl, smtplib, uuid
# from django.contrib.auth.forms import PasswordChangeForm
from datetime import datetime as dt
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import sigmoid_kernel
# from scipy import sparse
# from sklearn.metrics.pairwise import cosine_similarity
from datetime import date
from django.core.mail import send_mail
# Create your views here.


# user_pk = request.user.pk
# 	customer_account = User.objects.get(pk=user_pk)
# 	customer_details = CustomerAccountProfile.objects.get(userid=customer_account)
# 	this_user_genres = eval(customer_details.userfavouritegenre)
# 	this_user_genres.sort()
# 	this_user_genres = " ".join(this_user_genres)
# # 	this_user_favourite_book = Book.objects.filter(favourites__id=customer_details.pk)[::1]

# if(functionality=="add-to-favourites"):
# 				favourite_Book = Book.objects.filter(favourites__id=customer_details.pk)
# 				if(b1 not in favourite_Book):
# 					customer_details.favourites.add(b1)
# 					add_feature_value(isbn_13, "favourites_count")
# 					return HttpResponse("new_object")

def add_favourite_books():
	all_users = User.objects.all()
	for users in all_users:
		try:
			customer_account =  User.objects.get(pk=users.pk)
			customer_details = CustomerAccountProfile.objects.get(userid=customer_account)

			this_user_high_rated = Review.objects.filter(customerID=customer_details.pk).filter(rating_value=5).order_by('-rating_value')# |  Review.objects.filter(customerID=customer_details.pk).filter(rating_value=5).order_by('-rating_value')
			this_user_favourite_book = Book.objects.filter(favourites__id=customer_details.pk)
			the_books = [i.bookID for i in this_user_high_rated]

			# for books in the_books:
			# 	if books not in this_user_favourite_book:
			# 		customer_details.favourites.add(books)
		except:
			pass
def createaccount():
	file = open("names.txt", "r").readlines()
	file2 = open("genres.txt", "r").readlines()
	all_names = [names.replace("\n", "") for names in file]
	all_genres = [genres.replace("\n", "") for genres in file2]

	start_dt = date.today().replace(day=1, month=1).toordinal()
	end_dt = date.today().toordinal()

	def domains():
	    return random.choice(["@yahoo.com","@gmail.com","@hotmail.com","@outlook.com","@hotmail.fr"])

	def gender():
	    return random.choice(["Male", "Female"])

	for i in all_names:
		email = i.split(" ")[0].lower()+"."+i.split(" ")[1].lower()+str(random.randint(0,99))+domains()
		password ="Maideen69"
		first_name = i.split(" ")[0]
		last_name = i.split(" ")[1]
		birthDate = str(date.fromordinal(random.randint(start_dt, end_dt)))
		genders = gender()
		random_genre = random.sample(all_genres, random.randint(3, 9))
		random_genre.sort()
		random_genre = str(random_genre)
		print(username,email,password,first_name,last_name, birthDate,genders,random_genre)

		checkAccountExist = User.objects.filter(email=email)
		if(len(checkAccountExist)==0):
			user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name)
			print("New user object")

			#Creating the profile for the user
			user.customeraccountprofile_set.create(birthDate=birthDate, gender=genders, userfavouritegenre=random_genre)
			print("new customer profile object")

			listofgenre = eval(random_genre)
			genre_to_csv = " ".join(listofgenre)
			genre_to_csv = genre_to_csv.replace(",", "").replace("  ", " ").replace("-", " ")
			genre_to_csv = ''.join(e for e in genre_to_csv if e.isalnum() or e==" ")
			genre_to_csv = re.sub(" +", " ", genre_to_csv)
			genre_to_csv = unidecode.unidecode(genre_to_csv)

			with open('user_genre.csv', 'a') as csv_file:
				# Fields are user_id,genres
				towrite = "\n"+email+","+genre_to_csv
				csv_file.write(towrite)

		time.sleep(1)
def add_books_to_system(booksearch):
	response = requests.get("https://www.googleapis.com/books/v1/volumes?q="+booksearch)
	try:
		json_response = response.json()["items"]
		for book in json_response:
			try:
				if(len(book['volumeInfo']['industryIdentifiers'])==2):
					uid = book['id']
					etag = book['etag']
					title = book['volumeInfo']['title']

					if('authors' in  book['volumeInfo']):
						authors = book['volumeInfo']['authors']
						authors.sort()
						authors = ",".join(authors)
					else:
						authors = "None"

					if('publisher' in book['volumeInfo']):
						publisher = book['volumeInfo']['publisher']
					else:
						publisher = "None"

					if('publishedDate' in book['volumeInfo']):
						publishedDate = book['volumeInfo']['publishedDate']
					else:
						publishedDate = "None"

					if('description' in book['volumeInfo']):
						description = book['volumeInfo']['description']
					else:
						description = "None"

					ISBN_13 = None
					ISBN_10 = None
					if(book['volumeInfo']['industryIdentifiers'][0]['type'] == "ISBN_10"):
						ISBN_10 = book['volumeInfo']['industryIdentifiers'][0]['identifier']
					elif(book['volumeInfo']['industryIdentifiers'][0]['type'] == "ISBN_13"):
						ISBN_13 = book['volumeInfo']['industryIdentifiers'][0]['identifier']

					if(book['volumeInfo']['industryIdentifiers'][1]['type'] == "ISBN_10"):
						ISBN_10 = book['volumeInfo']['industryIdentifiers'][1]['identifier']
					elif(book['volumeInfo']['industryIdentifiers'][1]['type'] == "ISBN_13"):
						ISBN_13 = book['volumeInfo']['industryIdentifiers'][1]['identifier']

					if('categories' in book['volumeInfo']):
						categorie = book['volumeInfo']['categories']
						categories = [i.title().replace(",", " &").replace("  ", "") for i in categorie]
					else:
						categories = ["None"]

					if('averageRating' in book['volumeInfo']):
						averageRating = book['volumeInfo']['averageRating']
					else:
						averageRating = 0.0
					averageRating = round(averageRating,1)

					if('ratingsCount' in book['volumeInfo']):
						ratingsCount = book['volumeInfo']['ratingsCount']
					else:
						ratingsCount = 0

					print(ISBN_13)
					try:
						if('thumbnail' in book['volumeInfo']['imageLinks']):
							thumbnail = book['volumeInfo']['imageLinks']['thumbnail']
					except:
						thumbnail = "None"

					# if('thumbnail' in book['volumeInfo']['imageLinks']):
					# 	thumbnail = book['volumeInfo']['imageLinks']['thumbnail']
					# else:
					# 	thumbnail = "None"

					checkBookExist = Book.objects.filter(isbn_13=ISBN_13)
					if(len(checkBookExist)==0):
						print("New book")
						book_data = {"id": uid, "etag": etag, "title": title,
						"authors": authors, "publisher": publisher, "publishedDate": publishedDate,
						"description": description, "ISBN_10": ISBN_10, "ISBN_13": ISBN_13,
						"categories": categories, "averageRating": averageRating, "ratingsCount": ratingsCount,
						"thumbnail": thumbnail}

						Book.objects.create(isbn_13=ISBN_13, isbn_10=ISBN_10, title=title, book_data=book_data)
						print("Create New Book")

						book_genre = " ".join(categories)
						book_genre = book_genre.replace("&", "").replace("  ", " ")

						# Adding the genre/category to DB.
						category_db = "".join(categories)
						category_db = category_db.split("&")

						for item in category_db:
							if(item!="None"):
								split_item = list(item)
								if(split_item[0]==" "):
									split_item = split_item[1:]
								if(split_item[len(split_item)-1]==" "):
									split_item = split_item[:len(split_item)-1]
								item = "".join(split_item)
								item = item.replace(",", " ").replace("-", " ").replace("  ", " ")
								item = ''.join(e for e in item if e.isalnum() or e==" ")
								item = re.sub(" +", " ", item)
								item = unidecode.unidecode(item)
								checkGenreExist = Category.objects.filter(name=item)
								if(len(checkGenreExist)==0):
									Category.objects.create(name=item)

						with open('book_rating.csv', 'a') as br_writer, open('book_info.csv', 'a') as bi_writer, open('book_description.csv', 'a') as bd_writer:
							# Fields are isbn_13,book_genre,favourites_count,reading_now_count,to_read_count,have_read_count,average_rating,rating_count
							br_write = "\n"+ISBN_13+","+book_genre+","+"0"+","+"0"+","+"0"+","+"0"+","+str(2*averageRating)+","+str(ratingsCount)
							
							# Fields are isbn_13,title,authors,publisher,publishedDate
							authors = authors.replace(",", " ").replace("-", " ").replace("–", " ")
							authors = ''.join(e for e in authors if e.isalnum() or e==" ")
							authors = re.sub(" +", " ", authors)
							authors = unidecode.unidecode(authors)

							publisher = publisher.replace(",", " ").replace("-", " ").replace("–", " ")
							publisher = ''.join(e for e in publisher if e.isalnum() or e==" ")
							publisher = re.sub(" +", " ", publisher)
							publisher = unidecode.unidecode(publisher)

							title = title.replace(",", " ").replace("-", " ").replace("–", " ")
							title = ''.join(e for e in title if e.isalnum() or e==" ")
							title = re.sub(" +", " ", title)
							title = unidecode.unidecode(title)
							#Use regular expression to allow letters numbers and brackets
							bi_write = "\n"+ISBN_13+","+title+","+authors+","+publisher.title()+","+publishedDate.replace("-","/")

							description = description.replace(",", " ").replace("-", " ").replace("–", " ")
							description = ''.join(e for e in description if e.isalnum() or e==" ")
							description = re.sub(" +", " ", description)
							description = unidecode.unidecode(description)
							bd_write = "\n"+ISBN_13+","+description

							br_writer.write(br_write)
							bi_writer.write(bi_write)
							bd_writer.write(bd_write)
			except:
				pass
	except:
		pass
	return

@csrf_exempt
def index(request):

	##//
	# This code is for to adding 2000000 books to the database
	# with open("BX-Books.csv","r") as reader:
	# 	for row in reader:
	# 		line = row.split(";")[1].replace('"',"")
	# 		print(line)
	# 		add_books_to_system(line)
	##//

	start_time = time.time()
	metric = Metrics.objects.all()[0].metrics_data

	if request.method == "POST":
		metric["post_request_count"]+=1
		Metrics.objects.filter(id=1).update(metrics_data=metric)
		
		booksearch = request.POST['booksearch']
		response = requests.get("https://www.googleapis.com/books/v1/volumes?q="+booksearch)
		requested_books = []
		try:
			json_response = response.json()["items"]
			for book in json_response:
				try:
					if(len(book['volumeInfo']['industryIdentifiers'])==2):
						uid = book['id']
						etag = book['etag']
						title = book['volumeInfo']['title']

						if('authors' in  book['volumeInfo']):
							authors = book['volumeInfo']['authors']
							authors.sort()
							authors = ",".join(authors)
						else:
							authors = "None"

						if('publisher' in book['volumeInfo']):
							publisher = book['volumeInfo']['publisher']
						else:
							publisher = "None"

						if('publishedDate' in book['volumeInfo']):
							publishedDate = book['volumeInfo']['publishedDate']
						else:
							publishedDate = "None"

						if('description' in book['volumeInfo']):
							description = book['volumeInfo']['description']
						else:
							description = "None"

						ISBN_13 = None
						ISBN_10 = None
						if(book['volumeInfo']['industryIdentifiers'][0]['type'] == "ISBN_10"):
							ISBN_10 = book['volumeInfo']['industryIdentifiers'][0]['identifier']
						elif(book['volumeInfo']['industryIdentifiers'][0]['type'] == "ISBN_13"):
							ISBN_13 = book['volumeInfo']['industryIdentifiers'][0]['identifier']

						if(book['volumeInfo']['industryIdentifiers'][1]['type'] == "ISBN_10"):
							ISBN_10 = book['volumeInfo']['industryIdentifiers'][1]['identifier']
						elif(book['volumeInfo']['industryIdentifiers'][1]['type'] == "ISBN_13"):
							ISBN_13 = book['volumeInfo']['industryIdentifiers'][1]['identifier']

						if('categories' in book['volumeInfo']):
							categorie = book['volumeInfo']['categories']
							categories = [i.title().replace(",", " &").replace("  ", "") for i in categorie]
						else:
							categories = ["None"]

						if('averageRating' in book['volumeInfo']):
							averageRating = book['volumeInfo']['averageRating']
						else:
							averageRating = 0.0
						averageRating = round(averageRating,1)

						if('ratingsCount' in book['volumeInfo']):
							ratingsCount = book['volumeInfo']['ratingsCount']
						else:
							ratingsCount = 0

						try:
							if('thumbnail' in book['volumeInfo']['imageLinks']):
								thumbnail = book['volumeInfo']['imageLinks']['thumbnail']
						except:
							thumbnail = "None"

						checkBookExist = Book.objects.filter(isbn_13=ISBN_13)
						if(len(checkBookExist)==0):
							print("New book")
							book_data = {"id": uid, "etag": etag, "title": title,
							"authors": authors, "publisher": publisher, "publishedDate": publishedDate,
							"description": description, "ISBN_10": ISBN_10, "ISBN_13": ISBN_13,
							"categories": categories, "averageRating": averageRating, "ratingsCount": ratingsCount,
							"thumbnail": thumbnail}

							book_genre = " ".join(categories)
							book_genre = book_genre.replace("&", "").replace("  ", " ")

							# Adding the genre/category to DB.
							category_db = "".join(categories)
							category_db = category_db.split("&")

							for item in category_db:
								if(item!="None"):
									split_item = list(item)
									if(split_item[0]==" "):
										split_item = split_item[1:]
									if(split_item[len(split_item)-1]==" "):
										split_item = split_item[:len(split_item)-1]
									item = "".join(split_item)
									item = item.replace(",", " ").replace("-", " ").replace("  ", " ")
									item = ''.join(e for e in item if e.isalnum() or e==" ")
									item = re.sub(" +", " ", item)
									item = unidecode.unidecode(item)
									checkGenreExist = Category.objects.filter(name=item)
									if(len(checkGenreExist)==0):
										Category.objects.create(name=item)

							with open('book_rating.csv', 'a') as br_writer, open('book_info.csv', 'a') as bi_writer, open('book_description.csv', 'a') as bd_writer:
								# Fields are isbn_13,book_genre,favourites_count,reading_now_count,to_read_count,have_read_count,average_rating,rating_count
								br_write = "\n"+ISBN_13+","+book_genre+","+"0"+","+"0"+","+"0"+","+"0"+","+str(2*averageRating)+","+str(ratingsCount)
								
								# Fields are isbn_13,title,authors,publisher,publishedDate
								authors = authors.replace(",", " ").replace("-", " ").replace("–", " ")
								authors = ''.join(e for e in authors if e.isalnum() or e==" ")
								authors = re.sub(" +", " ", authors)
								authors = unidecode.unidecode(authors)

								publisher = publisher.replace(",", " ").replace("-", " ").replace("–", " ")
								publisher = ''.join(e for e in publisher if e.isalnum() or e==" ")
								publisher = re.sub(" +", " ", publisher)
								publisher = unidecode.unidecode(publisher)

								title = title.replace(",", " ").replace("-", " ").replace("–", " ")
								title = ''.join(e for e in title if e.isalnum() or e==" ")
								title = re.sub(" +", " ", title)
								title = unidecode.unidecode(title)
								#Use regular expression to allow letters numbers and brackets
								bi_write = "\n"+ISBN_13+","+title+","+authors+","+publisher.title()+","+publishedDate.replace("-","/")

								description = description.replace(",", " ").replace("-", " ").replace("–", " ")
								description = ''.join(e for e in description if e.isalnum() or e==" ")
								description = re.sub(" +", " ", description)
								description = unidecode.unidecode(description)
								bd_write = "\n"+ISBN_13+","+description

								br_writer.write(br_write)
								bi_writer.write(bi_write)
								bd_writer.write(bd_write)

								# Only create books when successfully written to csv
								Book.objects.create(isbn_13=ISBN_13, isbn_10=ISBN_10, title=title, book_data=book_data)
								print("Create New Book")
						requested_books.append(ISBN_13)
						# requested_books.append({"uid":uid, "averageRating":averageRating, "ratingsCount":ratingsCount, "authors":authors,"isbn_13": ISBN_13, "isbn_10": ISBN_10, "title": title, "thumbnail": thumbnail})
				except:
					pass
		except:
			pass
		required_book_objects = []
		for isbn_13 in requested_books:
			book_object = Book.objects.get(isbn_13=isbn_13)
			the_data = book_object.book_data
			required_book_objects.append({"uid":the_data["id"], "averageRating":the_data["averageRating"], "ratingsCount":the_data["ratingsCount"], "authors":the_data["authors"],"isbn_13": the_data["ISBN_13"], "isbn_10": the_data["ISBN_10"], "title": the_data["title"], "thumbnail": the_data["thumbnail"]})
		return render(request,"mainapp/frontpage.html", {"bookresults":required_book_objects,"booksearch":booksearch})
	#Can use this for displaying this items in book.html with tag: Book's with good ratings.
	try:
		average_rating_recommendation = weighted_average_and_favourite_score(request)
	except:
		average_rating_recommendation = []

	# Getting the recently added items
	all_books = Book.objects.all()
	top_20_books = all_books[len(all_books)-20:] if all_books.count()>20 else all_books[:]
	recently_added_books = []

	for items in top_20_books:
		the_data = items.book_data
		book_item = {"isbn_13": items.isbn_13, "isbn_10": items.isbn_10, "title": items.title, "thumbnail": the_data["thumbnail"]}
		recently_added_books.append(book_item)

	other_user_favourite_books = []
	if request.user.is_authenticated and not request.user.is_superuser:
		other_user_favourite_books = content_based_similar_user_items(request)

	# Metric update
	metric["total_page_visit"] +=1
	metric["get_request_count"] +=1
	metric["page_visit_counter"]["frontpage"]+=1

	duration = time.time() - start_time
	duration = int(duration * 1000)
	all_times = metric["page_load"]["frontpage"]
	all_times.append(duration)
	if(len(all_times)>50):
		all_times = all_times[-50:]
	metric["page_load"]["frontpage"] = all_times
	Metrics.objects.filter(id=1).update(metrics_data=metric)
	return render(request,'mainapp/frontpage.html',{"recently_added_books": recently_added_books,"average_rating_recommendation": average_rating_recommendation, "other_user_favourite_books": other_user_favourite_books,"carousel":True})

@csrf_exempt
def signup(request):
	start_time = time.time()
	metric = Metrics.objects.all()[0].metrics_data
	if request.method == 'POST':
		metric["post_request_count"] +=1
		Metrics.objects.filter(id=1).update(metrics_data=metric)
		fullname = request.POST['fullname']
		email = request.POST['email']
		password = request.POST['password']
		birthDate = request.POST['birthDate']
		gender = request.POST['gender']
		listOfUserGenre = str(request.POST['listofgenre'].split(","))

		# Checking if the password is secure.
		if(len(password)<8 or any(letter.isalpha() for letter in password)==False or any(capital.isupper() for capital in password)==False or any(number.isdigit() for number in password)==False):
			#any(letter.isalpha() for letter in password)==False is not necessary because if checking for capitals it should check
			#for letters as well.
			return HttpResponse("Password is not secure enough!")
		#Check if the account with same email id exist before creating a new one
		checkAccountExist = User.objects.filter(email=email)
		if(len(checkAccountExist)==0):
			fullname = fullname.split(" ")
			fname = " ".join(fullname[:len(fullname)-1]).title()
			sname = "".join(fullname[len(fullname)-1]).title()

			#Creating an account for the user
			user = User.objects.create_user(username=email, email=email, password=password, first_name=fname, last_name=sname)
			print("New user object")

			#Creating the profile for the user
			user.customeraccountprofile_set.create(birthDate=birthDate, gender=gender, userfavouritegenre=listOfUserGenre)
			print("new customer profile object")

			#Updating the genres to CSV for Data Mining
			listofgenre = eval(listOfUserGenre)
			listofgenre.sort()
			genre_to_csv = " ".join(listofgenre)
			genre_to_csv = genre_to_csv.replace(",", "").replace("  ", " ").replace("-", " ")
			genre_to_csv = ''.join(e for e in genre_to_csv if e.isalnum() or e==" ")
			genre_to_csv = re.sub(" +", " ", genre_to_csv)
			genre_to_csv = unidecode.unidecode(genre_to_csv)

			with open('user_genre.csv', 'a') as csv_file:
				# Fields are user_id,genres
				towrite = "\n"+email+","+genre_to_csv
				csv_file.write(towrite)

			# Metrics havent tested this
			domain_email = email.split("@")[1]
			if(domain_email not in metric["domains"]):
				metric["domains"][domain_email] = 1
			else:
				metric["domains"][domain_email] += 1
			Metrics.objects.filter(id=1).update(metrics_data=metric)
			#

			return render(request,'mainapp/login.html', {})#return redirect('mainapp:login')
		return HttpResponse("An account already exists for this email address, please try again!")
	#Retrive all the categories from the database
	all_categories = Category.objects.all()
	categories = [i.name for i in all_categories]
	categories.sort()
	metric["total_page_visit"] +=1
	metric["get_request_count"] +=1
	metric["page_visit_counter"]["signup"] +=1
	
	duration = time.time() - start_time
	duration = int(duration * 1000)
	all_times = metric["page_load"]["signup"]
	all_times.append(duration)
	if(len(all_times)>50):
		all_times = all_times[-50:]
	metric["page_load"]["signup"] = all_times
	Metrics.objects.filter(id=1).update(metrics_data=metric)
	if request.user.is_authenticated:
		return redirect("mainapp:index")
	return render(request,'mainapp/signup.html', {"categories": categories})

def login(request):
	start_time = time.time()
	metric = Metrics.objects.all()[0].metrics_data
	if request.method == 'POST':
		metric["post_request_count"] +=1
		email = request.POST['email']
		password = request.POST['password']

		user = authenticate(username=email, password=password)
		if user:
			auth_login(request, user)
			metric["total_login_count"] +=1
			metric["logged_in_user_count"] +=1
			Metrics.objects.filter(id=1).update(metrics_data=metric)
		else:
			return HttpResponse("Sorry! Username and Password didn't match, Please try again!")
	metric["total_page_visit"] +=1
	metric["get_request_count"] +=1
	metric["page_visit_counter"]["login"] +=1

	duration = time.time() - start_time
	duration = int(duration * 1000)
	all_times = metric["page_load"]["login"]
	all_times.append(duration)
	if(len(all_times)>50):
		all_times = all_times[-50:]
	metric["page_load"]["login"] = all_times

	Metrics.objects.filter(id=1).update(metrics_data=metric)
	if request.user.is_authenticated:
		return redirect("mainapp:index")
	return render(request,'mainapp/login.html', {})


def log_out(request):
	metric = Metrics.objects.all()[0].metrics_data
	metric["logged_in_user_count"] -=1
	metric["get_request_count"] +=1
	Metrics.objects.filter(id=1).update(metrics_data=metric)
	"""Log out - note that the session will be deleted"""
	request.session.flush()
	logout(request)
	return redirect('mainapp:index')

def passwordforgotten(request):
	start_time = time.time()
	metric = Metrics.objects.all()[0].metrics_data
	if request.method == 'POST':
		metric["post_request_count"] +=1
		Metrics.objects.filter(id=1).update(metrics_data=metric)

		email = request.POST['email'].lower()
		fullname = request.POST['fullname'].title()
		birthDate = request.POST['birthDate']

		fullname = fullname.split(" ")
		fname = " ".join(fullname[:len(fullname)-1])
		sname = "".join(fullname[len(fullname)-1])

		checkAccountExist = User.objects.filter(email=email)
		if(len(checkAccountExist)!=0):
			user_account = checkAccountExist[0]
			if(user_account.first_name==fname and user_account.last_name==sname and str(CustomerAccountProfile.objects.get(userid=user_account.pk).birthDate)==str(birthDate)):
				temporary_password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
				subject = 'Request to change password'
				message = """Hi {},\n\n You have recently request to change your account password. We have set a temporary password for your account. Please go to the login page and sign-in with your email and temporary password. One you are logged in, go to Profile under Account and enter a new strong password. \n\n Your Temporary Password is: {}""".format(" ".join(fullname), temporary_password)
				user_account.set_password(temporary_password)
				user_account.save()
				send_mail(subject,message,settings.EMAIL_HOST_USER,[email])
				metric["password_request_count"] +=1
				Metrics.objects.filter(id=1).update(metrics_data=metric)
		return render(request,'mainapp/resetpasswordconfirm.html',{})
	metric["total_page_visit"] +=1
	metric["get_request_count"] +=1
	metric["page_visit_counter"]["forgotpassword"] +=1

	duration = time.time() - start_time
	duration = int(duration * 1000)
	all_times = metric["page_load"]["forgotpassword"]
	all_times.append(duration)
	if(len(all_times)>50):
		all_times = all_times[-50:]
	metric["page_load"]["forgotpassword"] = all_times

	Metrics.objects.filter(id=1).update(metrics_data=metric)
	if request.user.is_authenticated:
		return redirect('mainapp:index')
	return render(request,'mainapp/forgotpassword.html',{})

@csrf_exempt
def update_profile(request):
	start_time = time.time()
	metric = Metrics.objects.all()[0].metrics_data
	user_pk = request.user.pk
	if not request.user.is_authenticated:#used to be if(not user_pk):
		return redirect('mainapp:login')

	#Return 404 page if no profile found
	try:
		customer_account = User.objects.get(pk=user_pk)
		customer_details = CustomerAccountProfile.objects.get(userid=customer_account)
	except CustomerAccountProfile.DoesNotExist:
		return redirect('mainapp:not_found')
	except User.DoesNotExist:
		return redirect('mainapp:login')

	fullname =  str(customer_account.first_name +" "+ customer_account.last_name)
	#Retrive all the categories from the database
	all_categories = Category.objects.all()
	categories = [i.name for i in all_categories]
	categories.sort()
	context = {"fullname": fullname,
				"email": customer_account.email,
				"userfavouritegenre": customer_details.userfavouritegenre,
				"categories": categories}

	if request.method == "PUT":
		metric["put_request_count"]+=1
		Metrics.objects.filter(id=1).update(metrics_data=metric)
		put = QueryDict(request.body)

		fullname = put.get('fullname').split(" ")
		fname = " ".join(fullname[:len(fullname)-1])
		sname = "".join(fullname[len(fullname)-1])
		email = put.get('email')
		listofgenre = str(put.get('listofgenre').split(","))

		User.objects.filter(pk=int(user_pk)).update(username=email, email=email, first_name=fname, last_name=sname)
		u = User.objects.get(pk=int(user_pk))

		if(put.get('password')):
			password = put.get('password')
			# User wants to change the password
			# Checking if the password is secure.
			if(len(password)<8 or any(letter.isalpha() for letter in password)==False or any(capital.isupper() for capital in password)==False or any(number.isdigit() for number in password)==False):
				#any(letter.isalpha() for letter in password)==False is not necessary because if checking for capitals it should check
				#for letters as well.
				return HttpResponse("Password is not secure enough!")
			u.set_password(put.get('password'))
			u.save()

		#Updating the user profile
		listofgenre = eval(listofgenre)
		listofgenre.sort()
		update_genre = str(listofgenre)
		CustomerAccountProfile.objects.filter(pk=int(customer_details.pk)).update(userfavouritegenre=update_genre)

		#Updating the genres to CSV for Data Mining
		#listofgenre = eval(listofgenre)
		#listofgenre.sort()

		genre_to_csv = " ".join(listofgenre)
		genre_to_csv = genre_to_csv.replace(",", "").replace("  ", " ").replace("-", " ")
		genre_to_csv = ''.join(e for e in genre_to_csv if e.isalnum() or e==" ")
		genre_to_csv = re.sub(" +", " ", genre_to_csv)
		genre_to_csv = unidecode.unidecode(genre_to_csv)

		with open('user_genre.csv', 'r') as reader, open('user_genre_temp.csv', 'w') as writer:
			for row in reader:
				row = row.split(",")
				if row[0] == email:
					# Fields are user_id,genres
					row[1] = genre_to_csv+"\n"
				row = ",".join(row)
				writer.write(row)

		#May have a probem with this techqnique if other function is using book_info because it erases the content
		with open('user_genre_temp.csv', 'r') as reader, open('user_genre.csv', 'w') as writer:
			for row in reader:
				writer.write(row)

		os.remove('user_genre_temp.csv')

		return HttpResponse("Your details are updated!")
	metric["total_page_visit"]+=1
	metric["get_request_count"]+=1
	metric["page_visit_counter"]["profilepage"]+=1

	duration = time.time() - start_time
	duration = int(duration * 1000)
	all_times = metric["page_load"]["profilepage"]
	all_times.append(duration)
	if(len(all_times)>50):
		all_times = all_times[-50:]
	metric["page_load"]["profilepage"] = all_times

	Metrics.objects.filter(id=1).update(metrics_data=metric)
	return render(request,'mainapp/profilepage.html', context)

def not_found(request):
	start_time = time.time()
	metric = Metrics.objects.all()[0].metrics_data
	metric["total_page_visit"] +=1
	metric["get_request_count"] +=1
	metric["page_visit_counter"]["notfound"] +=1

	duration = time.time() - start_time
	duration = int(duration * 1000)
	all_times = metric["page_load"]["notfound"]
	all_times.append(duration)
	if(len(all_times)>50):
		all_times = all_times[-50:]
	metric["page_load"]["notfound"] = all_times

	Metrics.objects.filter(id=1).update(metrics_data=metric)
	return render(request,'mainapp/404.html', {})

def permissiondenied(request):
	start_time = time.time()
	metric = Metrics.objects.all()[0].metrics_data
	metric["total_page_visit"] +=1
	metric["get_request_count"] +=1
	metric["page_visit_counter"]["permissiondenied"] +=1

	duration = time.time() - start_time
	duration = int(duration * 1000)
	all_times = metric["page_load"]["permissiondenied"]
	all_times.append(duration)
	if(len(all_times)>50):
		all_times = all_times[-50:]
	metric["page_load"]["permissiondenied"] = all_times

	Metrics.objects.filter(id=1).update(metrics_data=metric)
	return render(request,'mainapp/permissiondenied.html', {})

@csrf_exempt
def user_shelf(request):
	start_time = time.time()
	metric = Metrics.objects.all()[0].metrics_data

	user_pk = request.user.pk

	#Return 404 page if no shelf items are found for this profile
	#Need to return to login page if user not logged in when accessing shelf.
	try:
		customer_account = User.objects.get(pk=user_pk)
		customer_details = CustomerAccountProfile.objects.get(userid=customer_account)
	except CustomerAccountProfile.DoesNotExist:
		return redirect('mainapp:not_found')
	except User.DoesNotExist:
		return redirect('mainapp:login')

	# try:
	# 	customer_account = User.objects.get(pk=user_pk)
	# 	customer_details = CustomerAccountProfile.objects.get(userid=customer_account)
	# except:
	# 	return redirect('mainapp:login')

	#Need to check if the Book are already in favourites, reading now, to read and have read.
	favourite_Book = Book.objects.filter(favourites__id=customer_details.pk)
	reading_Book = Book.objects.filter(readingnow__id=customer_details.pk)
	to_read_Book = Book.objects.filter(toread__id=customer_details.pk)
	have_read_Book = Book.objects.filter(haveread__id=customer_details.pk)

	user_reviewed_Book = Review.objects.filter(customerID=customer_details.pk)
	user_visited_Book = []

	##Using session to retrive all the books the user has visited recently
	if 'history' not in request.session:
		request.session['history'] = []
	else:
		history = request.session['history']
		for items in history:
			user_visited_Book.append(Book.objects.get(isbn_13=items))

	# Ajax requests when the buttons are clicked to remove the books from the list.
	#Need to change this to delete REQUEST
	if request.method == "PUT":
		metric["put_request_count"]+=1
		Metrics.objects.filter(id=1).update(metrics_data=metric)
		put = QueryDict(request.body)
		functionality = put.get("functionality")
		objective = put.get("objective")# Not sure if this used in html and here
		isbn_13 = put.get("isbn_13")
		isbn_10 = put.get("isbn_10")

		#Need to add leading zero's to ISBN 10 and 13.
		# remaining_zero = "0"*(10-len(isbn_10))
		# isbn_10 = remaining_zero+isbn_10
		# remaining_zero = ""
		# remaining_zero = "0"*(13-len(isbn_13))
		# isbn_13 = remaining_zero+isbn_13

		#b1 = Book.objects.get(isbn_13=isbn_13, isbn_10=isbn_10)
		try:
			# Not sure if this is necessary or just leave it as  b1 = Book.objects.get(isbn_13=isbn_13)
			b1 = Book.objects.get(isbn_13=isbn_13)
		except Book.DoesNotExist:
			return redirect('mainapp:not_found')
		# b1 = Book.objects.get(isbn_13=isbn_13)

		if(functionality=="remove-from-favourites"):
			if(b1 in favourite_Book):
				customer_details.favourites.remove(b1)
				return HttpResponse("remove_object_success")
			return HttpResponse("remove_object_failure")
		elif(functionality=="remove-from-reading-now"):
			if(b1 in reading_Book):
				customer_details.readingnow.remove(b1)
				return HttpResponse("remove_object_success")
			return HttpResponse("remove_object_failure")
		elif(functionality=="remove-from-toread"):
			if(b1 in to_read_Book):
				customer_details.toread.remove(b1)
				return HttpResponse("remove_object_success")
			return HttpResponse("remove_object_failure")
		elif(functionality=="remove-from-haveread"):
			if(b1 in have_read_Book):
				customer_details.haveread.remove(b1)
				return HttpResponse("remove_object_success")
			return HttpResponse("remove_object_failure")

	#Get categories and average_rating for favourite_books from csv
	favourite_book = []
	reading_now_book = []
	toread_book = []
	haveread_book = []

	reviewed_Book = []
	visited_Book = []

	for i in favourite_Book:
		#line = get_row_from_csv(i.isbn_13, i.isbn_10)
		#categories = replace_last_occurence(line[7], '|', ' & ', 1)
		#categories = re.sub("[|]", ", ", categories)
		#book_attributes = {"isbn_13": i.isbn_13, "isbn_10": i.isbn_10, "title": i.title, "categories": categories, "average_rating": line[8]}
		#favourite_Book[i] = book_attributes
		#favourite_book.append(book_attributes)
		book_detail = i.book_data
		book_attributes = {"isbn_13": book_detail["ISBN_13"], "isbn_10": book_detail["ISBN_10"], "title": book_detail["title"], "categories": ",".join(book_detail["categories"]), "average_rating": book_detail["averageRating"]}
		# favourite_Book[i] = book_attributes
		favourite_book.append(book_attributes)

	for j in reading_Book:
		# line = get_row_from_csv(j.isbn_13, j.isbn_10)
		# categories = replace_last_occurence(line[7], '|', ' & ', 1)
		# categories = re.sub("[|]", ", ", categories)
		#book_attributes = {"isbn_13": j.isbn_13, "isbn_10": j.isbn_10, "title": j.title, "categories": categories, "average_rating": line[8]}
		#reading_Book[i] = book_attributes
		#reading_now_book.append(book_attributes)
		book_detail = j.book_data
		book_attributes = {"isbn_13": book_detail["ISBN_13"], "isbn_10": book_detail["ISBN_10"], "title": book_detail["title"], "categories": ",".join(book_detail["categories"]), "average_rating": book_detail["averageRating"]}
		# reading_Book[i] = book_attributes
		reading_now_book.append(book_attributes)

	for k in to_read_Book:
		# line = get_row_from_csv(k.isbn_13, k.isbn_10)
		# categories = replace_last_occurence(line[7], '|', ' & ', 1)
		# categories = re.sub("[|]", ", ", categories)
		#book_attributes = {"isbn_13": k.isbn_13, "isbn_10": k.isbn_10, "title": k.title, "categories": categories, "average_rating": line[8]}
		#to_read_Book[i] = book_attributes
		#toread_book.append(book_attributes)
		book_detail = k.book_data
		book_attributes = {"isbn_13": book_detail["ISBN_13"], "isbn_10": book_detail["ISBN_10"], "title": book_detail["title"], "categories": ",".join(book_detail["categories"]), "average_rating": book_detail["averageRating"]}
		# to_read_Book[i] = book_attributes
		toread_book.append(book_attributes)

	for l in have_read_Book:
		# line = get_row_from_csv(l.isbn_13, l.isbn_10)
		# categories = replace_last_occurence(line[7], '|', ' & ', 1)
		# categories = re.sub("[|]", ", ", categories)
		#book_attributes = {"isbn_13": l.isbn_13, "isbn_10": l.isbn_10, "title": l.title, "categories": categories, "average_rating": line[8]}
		#have_read_Book[i] = book_attributes
		#haveread_book.append(book_attributes)
		book_detail = l.book_data
		book_attributes = {"isbn_13": book_detail["ISBN_13"], "isbn_10": book_detail["ISBN_10"], "title": book_detail["title"], "categories": ",".join(book_detail["categories"]), "average_rating": book_detail["averageRating"]}
		# have_read_Book[i] = book_attributes
		haveread_book.append(book_attributes)

	for m in user_reviewed_Book:
		book_detail = m.bookID.book_data
		book_attributes = {"isbn_13": book_detail["ISBN_13"], "isbn_10": book_detail["ISBN_10"], "title": book_detail["title"], "categories": ",".join(book_detail["categories"]), "user_rating": m.rating_value, "description": m.description}
		reviewed_Book.append(book_attributes)

	for n in user_visited_Book:
		book_detail = n.book_data
		book_attributes = {"isbn_13": book_detail["ISBN_13"], "isbn_10": book_detail["ISBN_10"], "title": book_detail["title"], "categories": ",".join(book_detail["categories"]), "average_rating": book_detail["averageRating"]}
		visited_Book.append(book_attributes)

	# Collaborative Filtering
	personalized_books = pearson_correlation_collaborative_filtering(request)

	metric["total_page_visit"]+=1
	metric["get_request_count"]+=1
	metric["page_visit_counter"]["usershelf"]+=1

	duration = time.time() - start_time
	duration = int(duration * 1000)
	all_times = metric["page_load"]["usershelf"]
	all_times.append(duration)
	if(len(all_times)>50):
		all_times = all_times[-50:]
	metric["page_load"]["usershelf"] = all_times

	Metrics.objects.filter(id=1).update(metrics_data=metric)

	context = {'favourite_Book':favourite_book, 'reading_Book':reading_now_book, 'to_read_Book':toread_book, 'have_read_Book':haveread_book, 'reviewed_Book': reviewed_Book, 'visited_Book': visited_Book, 'personalized_books': personalized_books}
	return render(request,'mainapp/usershelf.html', context)

def get_row_from_csv(isbn_13, isbn_10):
	csv_file = csv.reader(open('book_info.csv', "r"), delimiter=",")
	for row in csv_file:
		if(row[1]==isbn_13 and row[2]==isbn_10):
			return row
	return None

def create_review():
	i = 0
	with open("user_rating.csv", "r") as reader:
		for lines in reader:
			try:
				lines = lines.replace("\n","").split(",")
				emails = lines[0]
				isbn_13 = lines[1]
				user_rating = int(eval(lines[2])/2)

				b1 = Book.objects.get(isbn_13=isbn_13)

				customer_account = User.objects.get(email=emails)
				customer_details = CustomerAccountProfile.objects.get(userid=customer_account)

				if(user_rating==2):
					user_review = random.choice(["Worst book ever!!!","I just don't get it!", "I wasted my time reading this.", "AWFUL"])
				elif(user_rating==4):
					user_review = random.choice(["Some confusion, but alright", "Could be better!", "MEh!!!!!!!", "Could have given better thought!!!"])
				elif(user_rating==6):
					user_review = random.choice(["This book is alright, but I wouldn't recommend this to anyone.", "OK I guess", "3/5 I would say"])
				elif(user_rating==8):
					user_review = random.choice(["I highly recommend this book to anyone","I liked the twist at the end!", "One of the best books I've ever read"])
				else:
					user_review = random.choice(["This author is the best","This book is AWESOME!", "I love this book"])

				created_date = dt.now()

				Review.objects.create(bookID=b1, customerID=customer_details, description=user_review, rating_value=user_rating, created_at=created_date)
				
				book_detail = b1.book_data

				new_rating_count = book_detail["ratingsCount"]+1

				#Calculating new average rating
				total_rating_points = book_detail["ratingsCount"]*book_detail["averageRating"]
				total_rating_points = total_rating_points+user_rating
				new_average_rating = round(total_rating_points/new_rating_count, 1)
				book_detail["ratingsCount"] = new_rating_count
				book_detail["averageRating"] = new_average_rating

				#Updating the database with the new rating count and new average rating value.
				Book.objects.filter(isbn_13=isbn_13).update(book_data=book_detail)
				i = i+1
				if(i%1000==0):
					print(i)
			except:
				pass
	#new_review = Review.objects.create(bookID=b1, customerID=customer_details, description=user_review, rating_value=user_rating, created_at=created_date)

@csrf_exempt
def book_page(request, isbn_13):
	start_time = time.time()
	metric = Metrics.objects.all()[0].metrics_data


	# if 'search_result' not in request.session:
	# 	request.session['search_result'] = []
	# else:
	# 	search_result = request.session['search_result']
	# 	if isbn_13 not in search_result:
	# 		search_result.append(isbn_13)
	# 	request.session['search_result'] = search_result
	##########################


	user_pk = request.user.pk

	if request.method == "PUT" and not user_pk:
		return HttpResponse("not_authenticated")

	if request.method == "POST" and not user_pk:
		return HttpResponse("not_authenticated")

	if request.user.is_superuser:
		if request.method == "PUT" or request.method == "POST":
			return HttpResponse("You cannot perform this action!")

	#Need to add leading zero's to ISBN 10 and 13.
	#remaining_zero = "0"*(10-len(isbn_10))
	#isbn_10 = remaining_zero+isbn_10
	# remaining_zero = ""
	# remaining_zero = "0"*(13-len(isbn_13))
	# isbn_13 = remaining_zero+isbn_13

	csv_file = csv.reader(open('book_info.csv', "r"), delimiter=",")
	# line = None

	# #Need threading to improve search efficiency
	# for row in csv_file:
	# 	if(row[1]==isbn_13 or row[2]==isbn_10):#used to be and instead of or
	# 		line = row
	# 		break
	# #Need to read file book_description file to get the description
	# file = open("book_descriptions.txt", "r").readlines()
	# description_line = None
	# for row in file:
	# 	c_line = row.split("|")
	# 	if((c_line[0]==isbn_13 or c_line[0]=="0"+isbn_13) and (c_line[1]==isbn_10 or c_line[1]=="0"+isbn_10)):
	# 		description_line = c_line[2].strip()
	# 		break

	#categories = replace_last_occurence(line[7], '|', ' & ', 1)#has some errors
	#categories = re.sub("[|]", ", ", line[7])

	#Set of books to display for suggestions.
	#item_based_recommendation = get_item_based_recommendation(csv_file)
	
	#Need to get all the reviews associated with the book.
	#b1 = Book.objects.get(isbn_13=isbn_13, isbn_10=isbn_10)
	# Redirecting to 404 page if book is not found
	try:
		b1 = Book.objects.get(isbn_13=isbn_13)
		#########################
		# Storing this book in the session for logged in users
		# may need to fix it becuase if user logs in first time and gets to the book page directly
		# then it only creates the session and does not store the isbn13 in the session unless if the user
		#refreshes the page again manually
		if request.user.is_authenticated:
			if 'history' not in request.session:
				request.session['history'] = []
			else:
				history = request.session['history']
				if isbn_13 not in history:
					history.append(isbn_13)
				request.session['history'] = history
		#########################
	except Book.DoesNotExist:
		return redirect('mainapp:not_found')
	average_rating_recommendation = weighted_average_and_favourite_score(request)# Not sure if this is used in book.html
	book_detail = b1.book_data
	#b1 = Book.objects.filter(isbn_13=isbn_13) | Book.objects.filter(isbn_10=isbn_10)
	book_reviews = Review.objects.filter(bookID=b1.pk)

	book_title = b1.title
	similar_books = content_based_similar_items(request, book_title)

	# Remocing this instance of the book from similar_books list
	similar_books = [i for i in similar_books if not (i['isbn_13'] == isbn_13)]

	# Verifying whether the comment is valid or not
	review_validity = []
	for i in book_reviews:
		the_customer = i.customerID
		customer_has_read_books = Book.objects.filter(haveread__id=the_customer.pk)
		if b1 in customer_has_read_books:
			comment_valid = True
		else:
			comment_valid = False
		review_validity.append(comment_valid)

	if user_pk and not request.user.is_superuser:# To allow admin to go into book page
		#If user is logged we can get more personal data
		# Initially below 2 lines were sufficient, but then the try/except is added.
		# customer_account = User.objects.get(pk=user_pk)
		# customer_details = CustomerAccountProfile.objects.get(userid=customer_account)

		#Return 404 page if no shelf items are found for this profile
		#Need to return to login page if user not logged in when accessing shelf.
		try:
			customer_account = User.objects.get(pk=user_pk)
			customer_details = CustomerAccountProfile.objects.get(userid=customer_account)
		except CustomerAccountProfile.DoesNotExist:
			return redirect('mainapp:not_found')
		except User.DoesNotExist:
			return redirect('mainapp:login')


		#b1 = Book.objects.get(isbn_13=isbn_13, isbn_10=isbn_10)
		# Ajax requests when the review button is clicked on the book.html
		if request.method == "POST":
			metric["post_request_count"]+=1
			Metrics.objects.filter(id=1).update(metrics_data=metric)
			functionality = request.POST['functionality']
			if functionality == "create-review":
				isbn_13 = request.POST['isbn_13']
				isbn_10 = request.POST['isbn_10']
				user_review = request.POST['user_review']#Need to sanitise the review
				user_rating = request.POST['user_rating']#Need to sanitise the review
				created_date = dt.now()
				new_review = Review.objects.create(bookID=b1, customerID=customer_details, description=user_review, rating_value=user_rating, created_at=created_date)
				full_name = customer_account.first_name + " " + customer_account.last_name
				response_items = ["revew_created_successfully&nbsp;", full_name+"&nbsp;", user_review+"&nbsp;", user_rating+"&nbsp;", str(created_date)+"&nbsp;", str(new_review.id)]
				
				new_rating_count = book_detail["ratingsCount"]+1

				#Calculating new average rating
				total_rating_points = book_detail["ratingsCount"]*book_detail["averageRating"]
				total_rating_points = total_rating_points+int(user_rating)
				new_average_rating = round(total_rating_points/new_rating_count, 1)
				book_detail["ratingsCount"] = new_rating_count
				book_detail["averageRating"] = new_average_rating

				#Updating the database with the new rating count and new average rating value.
				## Need to comment these below when unit testing
				Book.objects.filter(isbn_13=isbn_13).update(book_data=book_detail)
				#Writing review score to csv.
				with open('user_rating.csv', 'a') as csv_file:
					# Fields are uid,user_id,isbn_13,rating_score
					#towrite = "\n"+str(uuid.uuid1())+","+customer_account.email+","+isbn_13+","+str(float(2*int(user_rating)))
					towrite = "\n"+customer_account.email+","+isbn_13+","+str(float(2*int(user_rating)))
					csv_file.write(towrite)

				#Need to make adjustments to ratingscount and average rating in book_rating.csv
				with open('book_rating.csv', 'r') as reader, open('book_rating_temp.csv', 'w') as writer:
					#Fields: isbn_13,book_genre,favourites_count,reading_now_count,to_read_count,have_read_count,average_rating,rating_count
					for row in reader:
						row = row.split(",")
						if row[0] == isbn_13:
							row[6] = str(2*new_average_rating)# average_rating
							row[7] = str(new_rating_count)# rating_count
							row = ",".join(row)+"\n"
						else:
							row = ",".join(row)
						writer.write(row)

				#May have a probem with this techqnique if other function is using book_info because it erases the content
				## Try find a way to delete book_rating.csv and rename book_rating_temp.csv to book_rating.csv for better solution
				## current solution reads book_rating.csv, then writes to book_rating_temp.csv with changes.
				## then reads from book_rating_temp.csv, and then writing back to book_rating.csv

				with open('book_rating_temp.csv', 'r') as reader, open('book_rating.csv', 'w') as writer:
					for row in reader:
						writer.write(row)

				os.remove('book_rating_temp.csv')
				#os.rename('book_info_temp.csv', 'book_info.csv')
				return HttpResponse(response_items)

		#Ajax requests when user clicks like or dislikes the comment

		# Ajax requests when the one of the four buttons are clicked on the book.html
		if request.method == "PUT":
			metric["put_request_count"]+=1
			Metrics.objects.filter(id=1).update(metrics_data=metric)
			put = QueryDict(request.body)
			functionality = put.get("functionality")
			isbn_13 = put.get("isbn_13")
			isbn_10 = put.get("isbn_10")
			print(functionality)

			if(functionality=="add-to-favourites"):
				favourite_Book = Book.objects.filter(favourites__id=customer_details.pk)
				if(b1 not in favourite_Book):
					customer_details.favourites.add(b1)
					add_feature_value(isbn_13, "favourites_count")
					return HttpResponse("new_object")
				else:
					customer_details.favourites.remove(b1)
					subtract_feature_value(isbn_13, "favourites_count")
					return HttpResponse("remove_object")
			elif(functionality=="reading-now"):
				reading_Book = Book.objects.filter(readingnow__id=customer_details.pk)
				if(b1 not in reading_Book):
					customer_details.readingnow.add(b1)
					add_feature_value(isbn_13, "reading_now_count")
					return HttpResponse("new_object")
				else:
					customer_details.readingnow.remove(b1)
					subtract_feature_value(isbn_13, "reading_now_count")
					return HttpResponse("remove_object")
			elif(functionality=="to-read"):
				toread_Book = Book.objects.filter(toread__id=customer_details.pk)
				if(b1 not in toread_Book):
					customer_details.toread.add(b1)
					add_feature_value(isbn_13, "to_read_count")
					return HttpResponse("new_object")
				else:
					customer_details.toread.remove(b1)
					subtract_feature_value(isbn_13, "to_read_count")
					return HttpResponse("remove_object")
			elif(functionality=="have-read"):
				have_read_Book = Book.objects.filter(haveread__id=customer_details.pk)
				if(b1 not in have_read_Book):
					customer_details.haveread.add(b1)
					add_feature_value(isbn_13, "have_read_count")
					return HttpResponse("new_object")
				else:
					customer_details.haveread.remove(b1)
					subtract_feature_value(isbn_13, "have_read_count")
					return HttpResponse("remove_object")
			elif(functionality=="like-review"):
				review_id = put.get("review_id")
				this_review = Review.objects.get(id=int(review_id))
				list_of_liked = Review.objects.filter(likes__id=customer_details.pk)

				if(this_review not in list_of_liked):
					customer_details.likes.add(this_review)
					return HttpResponse("comment_like_added")
				else:
					customer_details.likes.remove(this_review)
					return HttpResponse("comment_like_reduced")
			elif(functionality=="dislike-review"):
				review_id = put.get("review_id")
				this_review = Review.objects.get(id=int(review_id))
				list_of_disliked = Review.objects.filter(dislikes__id=customer_details.pk)

				if(this_review not in list_of_disliked):
					customer_details.dislikes.add(this_review)
					return HttpResponse("comment_dislike_added")
				else:
					customer_details.dislikes.remove(this_review)
					return HttpResponse("comment_dislike_reduced")

		#Need to check if the Book are already in favourites, reading now, to read and have read.
		in_favourite_Book = Book.objects.filter(favourites__id=customer_details.pk)
		in_reading_Book = Book.objects.filter(readingnow__id=customer_details.pk)
		in_to_read_Book = Book.objects.filter(toread__id=customer_details.pk)
		in_have_read_Book = Book.objects.filter(haveread__id=customer_details.pk)

		in_favourite_Book = True if b1 in in_favourite_Book else False
		in_reading_Book = True if b1 in in_reading_Book else False
		in_to_read_Book = True if b1 in in_to_read_Book else False
		in_have_read_Book = True if b1 in in_have_read_Book else False

		# similar_books = []
		# if in_favourite_Book:
		# 	#This book is one of the favourite books of this user.
		# 	#So we can suggest similar book from this favourite book.
		# 	book_title = b1.title
		# 	similar_books = content_based_similar_items(request, book_title)
		# 	#Need to display this in the book.html
		# 	print(similar_books)


		context = {'isbn_13': book_detail["ISBN_13"], 'isbn_10': book_detail["ISBN_10"],
					'title': book_detail["title"], 'authors': book_detail["authors"],
					'publisher': book_detail["publisher"], 'publishedDate': book_detail["publishedDate"],
					'categories': ",".join(book_detail["categories"]), 'averageRating': book_detail["averageRating"],
					'ratingsCount': book_detail["ratingsCount"], 'thumbnail': book_detail["thumbnail"],
					'description': book_detail["description"], 'in_favourite_Book': in_favourite_Book,
					'in_reading_Book': in_reading_Book, 'in_to_read_Book': in_to_read_Book,
					'in_have_read_Book': in_have_read_Book, 'average_rating_recommendation': average_rating_recommendation,
					'book_reviews': book_reviews, 'review_validity': review_validity, 'similar_books': similar_books}

		# context = {'isbn_13':line[1], 'isbn_10': line[2],
		# 			'title': line[3], 'authors': line[4].replace("|", ","),
		# 			'publisher': line[5].replace("|", ","), 'publishedDate': line[6] ,
		# 			'categories': categories, 'averageRating': line[8],
		# 			'ratingsCount': line[9], 'thumbnail': line[14],
		# 			'description': description_line, 'in_favourite_Book': in_favourite_Book,
		# 			'in_reading_Book': in_reading_Book, 'in_to_read_Book': in_to_read_Book,
		# 			'in_have_read_Book': in_have_read_Book, 'item_based_recommendation': item_based_recommendation,
		# 			'book_reviews': book_reviews}
		metric["total_page_visit"]+=1
		metric["get_request_count"]+=1
		metric["page_visit_counter"]["book"]+=1

		duration = time.time() - start_time
		duration = int(duration * 1000)
		all_times = metric["page_load"]["book"]
		all_times.append(duration)
		if(len(all_times)>50):
			all_times = all_times[-50:]
		metric["page_load"]["book"] = all_times

		Metrics.objects.filter(id=1).update(metrics_data=metric)
		return render(request,'mainapp/book.html', context)

	context = {'isbn_13': book_detail["ISBN_13"], 'isbn_10': book_detail["ISBN_10"],
				'title': book_detail["title"], 'authors': book_detail["authors"],
				'publisher': book_detail["publisher"], 'publishedDate': book_detail["publishedDate"],
				'categories': ",".join(book_detail["categories"]), 'averageRating': book_detail["averageRating"],
				'ratingsCount': book_detail["ratingsCount"], 'thumbnail': book_detail["thumbnail"],
				'description': book_detail["description"], 'in_favourite_Book': False,
				'in_reading_Book': False, 'in_to_read_Book': False,
				'in_have_read_Book': False, 'average_rating_recommendation': average_rating_recommendation,
				'book_reviews': book_reviews, 'review_validity': review_validity, 'similar_books': similar_books}
	metric["total_page_visit"]+=1
	metric["get_request_count"]+=1
	metric["page_visit_counter"]["book"]+=1

	duration = time.time() - start_time
	duration = int(duration * 1000)
	all_times = metric["page_load"]["book"]
	all_times.append(duration)
	if(len(all_times)>50):
		all_times = all_times[-50:]
	metric["page_load"]["book"] = all_times
	
	Metrics.objects.filter(id=1).update(metrics_data=metric)
	return render(request,'mainapp/book.html', context)

def add_feature_value(isbn_13, feature):
	index_position = {"favourites_count": 2, "reading_now_count": 3,"to_read_count": 4,"have_read_count": 5}
	with open('book_rating.csv', 'r') as reader, open('book_rating_temp.csv', 'w') as writer:
		for row in reader:
			row = row.split(",")
			if row[0] == isbn_13:
				row[index_position[feature]] = str(int(row[index_position[feature]])+1)
			row = ",".join(row)
			writer.write(row)

	#May have a probem with this techqnique if other function is using book_info because it erases the content
	## Try find a way to delete book_rating.csv and rename book_rating_temp.csv to book_rating.csv for better solution
	## current solution reads book_rating.csv, then writes to book_rating_temp.csv with changes.
	## then reads from book_rating_temp.csv, and then writing back to book_rating.csv

	with open('book_rating_temp.csv', 'r') as reader, open('book_rating.csv', 'w') as writer:
		for row in reader:
			writer.write(row)
	os.remove('book_rating_temp.csv')
	#os.rename('book_info_temp.csv', 'book_info.csv')
	return

def subtract_feature_value(isbn_13, feature):
	index_position = {"favourites_count": 2, "reading_now_count": 3,"to_read_count": 4,"have_read_count": 5}
	with open('book_rating.csv', 'r') as reader, open('book_rating_temp.csv', 'w') as writer:
		for row in reader:
			row = row.split(",")
			if row[0] == isbn_13:
				row[index_position[feature]] = str(int(row[index_position[feature]])-1)
			row = ",".join(row)
			writer.write(row)

	#May have a probem with this techqnique if other function is using book_info because it erases the content
	## Try find a way to delete book_rating.csv and rename book_rating_temp.csv to book_rating.csv for better solution
	## current solution reads book_rating.csv, then writes to book_rating_temp.csv with changes.
	## then reads from book_rating_temp.csv, and then writing back to book_rating.csv

	with open('book_rating_temp.csv', 'r') as reader, open('book_rating.csv', 'w') as writer:
		for row in reader:
			writer.write(row)
	os.remove('book_rating_temp.csv')
	#os.rename('book_info_temp.csv', 'book_info.csv')
	return

def get_item_based_recommendation(csv_file):
	all_books = Book.objects.all()
	books_Objects2 = []
	books_Objects = []
	while(len(books_Objects)!=10):
		random_num = random.randint(0, len(all_books)-1)
		a_book = all_books[random_num]
		if a_book not in books_Objects2:
			books_Objects2.append(a_book)
			book_detail = a_book.book_data
			book_item = {"isbn_13": a_book.isbn_13, "isbn_10": a_book.isbn_10, "title": a_book.title, "thumbnail": book_detail["thumbnail"]}
			books_Objects.append(book_item)
	return books_Objects

def replace_last_occurence(s, old, new, occurrence):
	li = s.rsplit(old, occurrence)
	return new.join(li)

def content_based_similar_user_items(request):
	# Used in front_page under Favourite books from similar users'...
	users = pd.read_csv("user_genre.csv")
	tfv = TfidfVectorizer(min_df=3,  max_features=None, 
            strip_accents='unicode', analyzer='word',token_pattern=r'\w{1,}',
            ngram_range=(1, 3))

	
	tfv_matrix = tfv.fit_transform(users['genres'])# Fitting the TF-IDF on the 'genres' text
	sig = sigmoid_kernel(tfv_matrix, tfv_matrix)# Compute the sigmoid kernel

	# Reverse mapping of indices and book titles
	# If more than one user has same genre list, then considering one of them is sufficient.
	indices = pd.Series(users.index, index=users['genres']).drop_duplicates()

	def give_rec(title, sig=sig):
	    try:
	        idx = indices[title].iloc[0]
	    except:
	        idx = indices[title]
	    sig_scores = list(enumerate(sig[idx]))
	    sig_scores = sorted(sig_scores, key=lambda x: x[1], reverse=True)
	    sig_scores = sig_scores[1:11]
	    book_indices = [i[0] for i in sig_scores]
	    return users['genres'].iloc[book_indices]

	user_pk = request.user.pk
	customer_account = User.objects.get(pk=user_pk)
	customer_details = CustomerAccountProfile.objects.get(userid=customer_account)
	this_user_genres = eval(customer_details.userfavouritegenre)
	this_user_genres.sort()
	this_user_genres = " ".join(this_user_genres)
	this_user_favourite_book = Book.objects.filter(favourites__id=customer_details.pk)[::1]
	
	original_table = give_rec(this_user_genres)

	#Top 10 similar users
	book_df = list(users[users.genres.isin(list(original_table))]["user_id"])
	#Top 5 users who are similar to this user
	book_df = book_df[:5] if len(book_df)>5 else A[:]

	#Testing
	#book_df = ["hajam09@yahoo.com", "oliverqueen12@gmail.com"]
	###
	to_recommended_books = []
	for users in book_df:
		customer_account = User.objects.get(email=users)
		customer_details = CustomerAccountProfile.objects.get(userid=customer_account)
		favourite_Book = Book.objects.filter(favourites__id=customer_details.pk)
		to_recommended_books = to_recommended_books+favourite_Book[::1]

	#Remove duplicate book objects
	to_recommended_books = list(dict.fromkeys(to_recommended_books))
	final_result = []

	for i in range(len(to_recommended_books)):
		book_json = to_recommended_books[i].book_data
		if book_json['averageRating'] > 3.0:
			final_result.append({"isbn_13": to_recommended_books[i].isbn_13, "isbn_10": to_recommended_books[i].isbn_10, "title": to_recommended_books[i].title, "thumbnail": book_json["thumbnail"]})
	return final_result

def weighted_average_and_favourite_score(request):
	# Used in front_page under Books Based on Ratings...
	book_info = pd.read_csv("book_info.csv")
	book_rating = pd.read_csv("book_rating.csv")

	book_rating_merge = book_rating.merge(book_info, on='isbn_13')
	book_rating_cleaned = book_rating_merge.drop(columns=['reading_now_count', 'to_read_count', 'have_read_count'])

	#Implementing weighted average for each book's average rating // Non - personalized
	v = book_rating_cleaned['rating_count']
	R = book_rating_cleaned['average_rating']
	C = book_rating_cleaned['average_rating'].mean()
	m = book_rating_cleaned['rating_count'].quantile(0.70)

	book_rating_cleaned['weighted_average'] = ((R*v) + (C*m))/(v+m)

	book_sorted_ranking = book_rating_cleaned.sort_values('weighted_average', ascending=False)
	book_sorted_ranking[['isbn_13', 'title', 'book_genre', 'authors', 'publisher', 'average_rating', 'rating_count', 'weighted_average', 'favourites_count']]

	#Only implement this feature once the user has favourited their books and so on.
	by_favourites_count = book_sorted_ranking.sort_values('favourites_count', ascending=False)
	##

	#This is for recommending books to the users based on scaled weighting (50%) and favourites_count (50%).
	scaling = MinMaxScaler()
	book_scaled = scaling.fit_transform(book_rating_cleaned[['weighted_average', 'favourites_count']])
	book_normalized = pd.DataFrame(book_scaled, columns=['weighted_average', 'favourites_count'])

	book_rating_cleaned[['normalized_weight_average','normalized_popularity']]= book_normalized

	book_rating_cleaned['score'] = book_rating_cleaned['normalized_weight_average'] * 0.5 + book_rating_cleaned['normalized_popularity'] * 0.5
	books_scored_df = book_rating_cleaned.sort_values(['score'], ascending=False)
	final_result = books_scored_df[['isbn_13', 'title', 'normalized_weight_average', 'normalized_popularity', 'score']].head(15)

	list_of_isbn = list(final_result['isbn_13'])
	list_of_books = []

	for isbns in list_of_isbn:
		the_book = Book.objects.get(isbn_13=str(isbns))
		the_data = the_book.book_data
		book_item = {"isbn_13": the_book.isbn_13, "isbn_10": the_book.isbn_10, "title": the_book.title, "thumbnail": the_data["thumbnail"]}
		list_of_books.append(book_item)
	return list_of_books

def content_based_similar_items(request, title):
	# Used in book.html
	books = pd.read_csv("book_info.csv")
	rating = pd.read_csv("book_rating.csv")
	description = pd.read_csv("book_description.csv")

	books_df_merge = books.merge(rating, on='isbn_13')
	books_cleaned_df = books_df_merge.drop(columns=['reading_now_count', 'to_read_count', 'have_read_count'])
	books_cleaned_df = books_df_merge.merge(description, on='isbn_13')

	# Content Based Recommendation System
	# Make a recommendations based on the books’s description given in the description column.
	# So if our user gives us a book title, our goal is to recommend books that share similar description summaries.
	books_df_merge.drop(columns=['reading_now_count', 'to_read_count', 'have_read_count'])
	tfv = TfidfVectorizer(min_df=3,  max_features=None, 
            strip_accents='unicode', analyzer='word',token_pattern=r'\w{1,}',
            ngram_range=(1, 3),
            stop_words = 'english')

	books_cleaned_df['description'] = books_cleaned_df['description'].fillna('')# Filling NaNs with empty string
	tfv_matrix = tfv.fit_transform(books_cleaned_df['description'])# Fitting the TF-IDF on the 'overview' text
	sig = sigmoid_kernel(tfv_matrix, tfv_matrix)# Compute the sigmoid kernel
	indices = pd.Series(books_cleaned_df.index, index=books_cleaned_df['title']).drop_duplicates()# Reverse mapping of indices and book titles

	def give_rec(title, sig=sig):
	    # Get the index corresponding to title
	    try:
	        idx = indices[title].iloc[0]
	    except:
	        idx = indices[title]
	    sig_scores = list(enumerate(sig[idx]))# Get the pairwsie similarity scores 
	    sig_scores = sorted(sig_scores, key=lambda x: x[1], reverse=True)# Sort the books 
	    sig_scores = sig_scores[1:11]# Scores of the 10 most similar books
	    book_indices = [i[0] for i in sig_scores]# Book indices
	    return books_cleaned_df['title'].iloc[book_indices]# Top 10 most similar books

	# Testing our content-based recommendation system with the seminal film Of Mice and Men
	#Loop thorugh user favourite book title/title of the user favourite book
	title = title.replace(",", "").replace("-", "").replace("–", "")
	title = ''.join(e for e in title if e.isalnum() or e==" ")
	title = re.sub(" +", " ", title)
	title = unidecode.unidecode(title)
	original_table = give_rec(title)

	books_cleaned_df = books_cleaned_df[books_cleaned_df.title.isin(list(original_table))]
	books_cleaned_df.drop(columns=['publisher','publishedDate','favourites_count','reading_now_count','to_read_count','have_read_count','have_read_count'])

	isbns_columns = books_cleaned_df["isbn_13"]
	all_similar_books = list(isbns_columns)

	list_of_books = []
	for isbn_13 in all_similar_books:
		the_book = Book.objects.get(isbn_13=str(isbn_13))
		the_data = the_book.book_data
		book_item = {"isbn_13": the_book.isbn_13, "isbn_10": the_book.isbn_10, "title": the_book.title, "thumbnail": the_data["thumbnail"]}
		list_of_books.append(book_item)
	return list_of_books
	#return [Book.objects.get(isbn_13=isbn_13) for isbn_13 in all_similar_books]

def pearson_correlation_collaborative_filtering(request):
	# Used in user_shelf
	ratings = pd.read_csv('user_rating.csv')
	books = pd.read_csv('book_info.csv')
	ratings = pd.merge(books,ratings).drop(['authors','publisher','publishedDate'],axis=1)

	userRatings = ratings.pivot_table(index=['user_id'],columns=['title'],values='rating_score')
	# Fixing books that have less than 10 user ratings. Uncomment this in the future
	#userRatings = userRatings.dropna(thresh=10, axis=1).fillna(0,axis=1)
	corrMatrix = userRatings.corr(method='pearson')

	def get_similar(book_name,rating):
	    similar_ratings = corrMatrix[book_name]*(rating-2.5)
	    similar_ratings = similar_ratings.sort_values(ascending=False)
	    return similar_ratings

	# Getting user's top rated books
	user_pk = request.user.pk
	customer_account = User.objects.get(pk=user_pk)
	customer_details = CustomerAccountProfile.objects.get(userid=customer_account)
	user_high_reviews = Review.objects.filter(customerID=customer_details.pk).filter(rating_value=4).order_by('-rating_value') |  Review.objects.filter(customerID=customer_details.pk).filter(rating_value=5).order_by('-rating_value')
	#May not need this because user would only reate once, check.
	unique_books = []
	mining_books = []
	
	for items in user_high_reviews:
		if(items.bookID.isbn_13 not in unique_books):
			unique_books.append(items.bookID.isbn_13)

			title = items.bookID.title
			title = title.replace(",", "").replace("-", "").replace("–", "")
			title = ''.join(e for e in title if e.isalnum() or e==" ")
			title = re.sub(" +", " ", title)
			title = str(unidecode.unidecode(title))
			mining_books.append((title, 2.0*items.rating_value))
	top_10_books = mining_books[len(mining_books)-10:] if len(mining_books)>10 else mining_books[:]

	similar_books = pd.DataFrame()
	for book, rating in top_10_books:
		try:
			similar_books = similar_books.append(get_similar(book,rating),ignore_index = True)
		except:
			pass

	top_recommended_books = similar_books.sum().sort_values(ascending=False).head(20)
	top_book_titles = [top_recommended_books[top_recommended_books==i].index[0] for i in top_recommended_books]
	top_book_objects = [Book.objects.filter(title__icontains=titles.strip().lower())  for titles in top_book_titles]

	list_of_books = []

	for isbn_13 in top_book_objects:
		try:
			book_object = isbn_13[0]
			the_data = book_object.book_data
			if(the_data["averageRating"]>=3):
				book_item = {"isbn_13": book_object.isbn_13, "isbn_10": book_object.isbn_10, "title": book_object.title, "average_rating": the_data["averageRating"], "categories": ",".join(the_data["categories"])}
				list_of_books.append(book_item)
		except Exception as e:
			pass
	return list_of_books

def add_user_country_browser(request):
	if request.method == "POST":
		user_country = request.POST["user_country"]
		user_browser = request.POST["user_browser"]
		metric = Metrics.objects.all()[0].metrics_data
		if "user_data" not in request.session:
			request.session["user_data"] = [user_country, user_browser]
			if(user_country in metric["countries"]):
				metric["countries"][user_country] +=1
			else:
				metric["countries"][user_country] = 1
			if(user_browser in metric["browser"]):
				metric["browser"][user_browser] +=1
			else:
				metric["browser"][user_browser] = 1

		Metrics.objects.filter(id=1).update(metrics_data=metric)
		return HttpResponse("Added")
	return

def dashboard_live_data(request):
	records = Metrics.objects.all()[0].metrics_data
	records["page_visit_counter"]["signup"] = records["page_visit_counter"]["signup"]//2 # Makes two requests on each refresh
	records["user_count"] = User.objects.all().count()
	records["book_count"] = Book.objects.all().count()
	records["reviews_count"] = Review.objects.all().count()
	records["today_member_count"] = User.objects.filter(last_login__startswith=timezone.now().date()).count()
	records["db_size"] = round(os.stat(os.getcwd()+"\\db.sqlite3").st_size*0.000001,2)
	return JsonResponse(records)

def dashboard(request):
	# add_user_country_browser(request)
	metric = Metrics.objects.all()[0].metrics_data
	metric["total_page_visit"]+=1
	Metrics.objects.filter(id=1).update(metrics_data=metric)
	if not request.user.is_authenticated:
		return redirect('mainapp:login')
	if not request.user.is_superuser:
		return redirect('mainapp:permissiondenied')
	records = Metrics.objects.all()[0].metrics_data
	records["page_visit_counter"]["signup"] = records["page_visit_counter"]["signup"]//2 # Makes two requests on each refresh
	records["user_count"] = User.objects.all().count()
	records["book_count"] = Book.objects.all().count()
	records["reviews_count"] = Review.objects.all().count()
	records["today_member_count"] = User.objects.filter(last_login__startswith=timezone.now().date()).count()
	try:
		records["db_size"] = round(os.stat(os.getcwd()+"\\db.sqlite3").st_size*0.000001,2)
	except:
		records["db_size"] = None
	return render(request,'mainapp/dashboard.html', records)