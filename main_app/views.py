from django.shortcuts import render,redirect
from datetime import timedelta, datetime

from django.conf import settings 
user_details = settings.MONGO_DB.userdata
user_sessions = settings.MONGO_DB.sessions


from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# Create your views here.
def index(request):
    return redirect("/Home/")

def home(request):
    cutoff = datetime.now() - timedelta(minutes=15)
    user_details.delete_many({
        "isVerified" : False, 
        "Creation_Time" : {"$lt": cutoff}
    })

    if request.session.get("user_id"):
        if request.method == "POST":
            name = request.POST.get("Name")
            Email = request.POST.get("Email")
            Message = request.POST.get("Msg")
            value = {
                "user_name" : name,
                "user_email" : Email,
                "user_message" : Message,
                "domain" : request.build_absolute_uri('/')
                }
            subject = 'Copy of Your Response'
            html_message = render_to_string('Email_template/contact_email_template.html',value)
            email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email='spendserver@gmail.com',
                to=['spendserver@gmail.com',Email],
            )
            email.content_subtype = 'html'  # To send HTML content
            email.send()
            return redirect("/Home/")
        
        context = {
            "isLogin" : True,
            "id" : request.session.get("user_id")
        }
        return render(request,"home.html",context)
    else:
        if request.method == "POST":
            name = request.POST.get("Name")
            Email = request.POST.get("Email")
            Message = request.POST.get("Msg")
            value = {
                "user_name" : name,
                "user_email" : Email,
                "user_message" : Message,
                "domain" : request.build_absolute_uri('/')
                }
            subject = 'Copy of Your Response'
            html_message = render_to_string('Email_template/contact_email_template.html',value)
            email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email='spendserver@gmail.com',
                to=['spendserver@gmail.com',Email],
            )
            email.content_subtype = 'html'  # To send HTML content
            email.send()
            return redirect("/Home/")
        
        context = {
            "isLogin" : False
        }   
        return render(request,"home.html",context)