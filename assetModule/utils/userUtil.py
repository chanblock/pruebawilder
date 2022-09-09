from pickle import TRUE
import smtplib
from pymongo import MongoClient
from datetime import datetime

from django.contrib import messages
from chanblockweb.settings.base import env


# client = MongoClient()
# db = client.messari.prueba1
# client = MongoClient('mongodb+srv://admin:uINsqkhy8mrC4rv2@clusterchanblock.9rmo2.mongodb.net/?retryWrites=true&w=majority')
client = MongoClient(env('MONGOATLAS_USER'))
db = client.chancblock.emailUser

def register_email_ajax(request):
    values=dict()
    for value in request.POST:
        values[value]=request.POST[value]
    values.pop('csrfmiddlewaretoken')
    db.insert_one(values)
    cofirm_register(values['email'])
    return ('save')

def register_email(request):
    values=dict()
    for value in request.POST:
        values[value]=request.POST[value]
    values.pop('csrfmiddlewaretoken')
    emaildb= list(db.find({'email': values['email']}))
    if emaildb:

        messages.error(request,"You email exist")
        
    else:
        db.insert_one(values)
        messages.success(request,"You email registered successfully")
        cofirm_register(values['email'])
        return TRUE
      





def cofirm_register(email):
    message = 'Your email has been successfully registered. We will be communicating the latest news from MTgox'
    subject = 'Chanblock: mail registration successful'

    message = 'Subject: {}\n\n{}'.format(subject, message)

    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login ('info.chanblock@gmail.com',env('EMAIL_PASSWORD'))

    server.sendmail('info.chanblock@gmail.com',email,message)

    server.quit()

    print("Correo enviado exitosamente!")