from django.shortcuts import render,redirect
import random
from datetime import datetime
from bson import ObjectId

from django.core.mail import EmailMessage
from django.template.loader import render_to_string

import requests
import json
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests


from django.conf import settings 
user_details = settings.MONGO_DB.userdata
user_sessions = settings.MONGO_DB.sessions



# pip install pyyaml ua-parser user-agents
from user_agents import parse



def get_client_ip(request):
    # Check if behind a proxy (like Nginx or a load balancer)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_device_info(request):
    ua_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(ua_string)

    device_type = "Mobile" if user_agent.is_mobile else \
                  "Tablet" if user_agent.is_tablet else \
                  "PC" if user_agent.is_pc else \
                  "Other"

    browser = user_agent.browser.family      # e.g., Chrome, Safari
    os = user_agent.os.family                # e.g., Windows, iOS, Android

    response_text = (
        device_type +"&"+ browser +"&"+ os
    )
    return response_text




# 6 Digit OTP means normal otp validation
# OTP = 0 means , Login with google
# OTP = 1 means , First Generate OTP and then login with google





def genOTP(request,email):
    temp = random.randint(100000,999999)
    subject = 'Your OTP Verification Code'
    html_message = render_to_string('Email_template/otp_email_template.html', {'otp': temp, "domain" : request.build_absolute_uri('/')})
    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email='spendserver@gmail.com',
        to=[email],
    )
    email.content_subtype = 'html'  # To send HTML content
    email.send()
 
    return(temp)

# Create your views here.
def signin(request):
    if request.session.get("user_id"):
        url = "/Dashboard/Home/" + request.session.get("user_id") + "/"
        return redirect(url)
    
    if request.method == "POST":
        useremail = request.POST.get("mail")
        if user_details.find_one({"Email" : useremail}):
            user_details.update_one(
                {"Email" : useremail},
                {"$set" : {"OTP" : genOTP(request,useremail),
                "Last_loging_Time" : datetime.now()
                }})
        else:
            user_details.insert_one({
                "Email" : useremail,
                "OTP" : genOTP(request,useremail),
                "Creation_Time" : datetime.now(),
                "Last_loging_Time" : datetime.now(),
                "isVerified" : False
            })

        user = user_details.find_one({"Email" : useremail})
        userid = str(user["_id"])

        url = "/Auth/OTP/" + userid + "/"
        return redirect(url)
    
    return render(request, 'Auth/login.html')

def checkOTP(request,userid):
    try:
        if request.session.get("user_id"):
            url = "/Dashboard/Home/" + request.session.get("user_id") + "/"
            return redirect(url)
        
        user = user_details.find_one({"_id" : ObjectId(userid)})
        if request.method == "POST":
            otp = request.POST.get("otp")
            if len(otp) != 6:
                context = {
                    "msg" : "OTP Should be 6 Digits."
                }
                return render(request,"Auth/otp_verification.html", context)
            
            elif user["OTP"] != int(otp):
                context = {
                    "msg" : "Please Enter Valid OTP Details."
                }
                return render(request,"Auth/otp_verification.html", context)
            
            else:
                request.session["user_id"] = userid
                request.session["user_email"] = user["Email"]

                if user_details.find_one({"Email" : user["Email"], "isVerified" : False}):
                    subject = 'Welcome to Spend Server'
                    html_message = render_to_string('Email_template/welcome_email_template.html', {"domain" : request.build_absolute_uri('/')})
                    email = EmailMessage(
                        subject=subject,
                        body=html_message,
                        from_email='spendserver@gmail.com',
                        to=[user["Email"]],
                    )
                    email.content_subtype = 'html'  # To send HTML content
                    email.send()
                    
                                    
                user_details.update_one(
                    {"Email" : user["Email"]},
                    {"$set" : {"isVerified" : True}}
                    )
                
                redirect_url = request.session.get("url")
                if redirect_url:
                    url = redirect_url
                else:
                    url = "/Dashboard/Home/" + userid + "/"

                device_info = get_device_info(request)
                device_type, browser, os = device_info.split("&")

                if not user_sessions.find_one({
                    "UserId" : userid,
                    "Network_ip" : get_client_ip(request),
                    "Device_Type" : device_type,
                    "Browser" : browser,
                    "OS" : os,
                }):
                    user_sessions.insert_one({
                        "UserId" : userid,
                        "Network_ip" : get_client_ip(request),
                        "Device_Type" : device_type,
                        "Browser" : browser,
                        "OS" : os,
                        "Log_Time" : datetime.now()
                    })
                else:
                    user_sessions.update_one({
                        "UserId" : userid,
                        "Network_ip" : get_client_ip(request),
                        "Device_Type" : device_type,
                        "Browser" : browser,
                        "OS" : os,},
                        {"$set" : {"Log_Time" : datetime.now()
                    }})
                    
                return redirect(url)     
            
        return render(request, 'Auth/otp_verification.html')
    
    except:
        return redirect("/Home/")
    

def signout(request):
    request.session.flush()
    return redirect("/Auth/Login/")



def google(request): 
    if request.session.get("user_id"): 
        return redirect("/Home/") 
    
    code = request.GET.get('code') # Handle the Google callback 
    if not code: 
        print("No_Code") 
        return redirect("Login") 
    print("Code Recived...") 
    # Exchange the authorization code for tokens 
    token_url = "https://oauth2.googleapis.com/token" 
    data = { 
        'code': code, 
        'client_id': settings.GOOGLE_OAUTH_CLIENT_ID, 
        'client_secret': settings.GOOGLE_OAUTH_CLIENT_SECRET, 
        'redirect_uri': settings.GOOGLE_REDIRECT_URI, 
        'grant_type': 'authorization_code', 
        } 
 
    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        tokens = response.json()

        print("Token response:", json.dumps(tokens, indent=2))

        email = None

        if 'id_token' in tokens:
            idinfo = id_token.verify_oauth2_token(
                tokens['id_token'],
                google_requests.Request(),
                settings.GOOGLE_OAUTH_CLIENT_ID
            )
            email = idinfo['email']
        elif 'access_token' in tokens:
            userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
            userinfo_response = requests.get(userinfo_url, headers=headers)
            userinfo_response.raise_for_status()
            user_info = userinfo_response.json()
            email = user_info['email']
        else:
            print("No id_token or access_token")
            return redirect("/Auth/Login/")

        if not email:
            print("Email not found in token response")
            return redirect("/Auth/Login/")

        # ✅ MongoDB: Save or get user
        user = user_details.find_one({"Email": email})
        if not user:
            user_details.insert_one({
                "Email": email,
                "OTP": 0,
                "Creation_Time": datetime.now(),
                "Last_loging_Time": datetime.now(),
                "isVerified": True
            })

            user = user_details.find_one({"Email": email})

            subject = 'Welcome to Spend Server'
            html_message = render_to_string('Email_template/welcome_email_template.html', {"domain" : request.build_absolute_uri('/')})
            email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email='spendserver@gmail.com',
                to=[email],
            )
            email.content_subtype = 'html'  # To send HTML content
            email.send()


        elif user["isVerified"] == False : 
            user_details.update_one(
                {"Email" : email},
                {"$set" : {
                    "isVerified" : True,
                    "OTP" : 1
                }}
            )
            user = user_details.find_one({"Email": email})

            subject = 'Welcome to Spend Server'
            html_message = render_to_string('Email_template/welcome_email_template.html', {"domain" : request.build_absolute_uri('/')})
            email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email='spendserver@gmail.com',
                to=[email],
            )
            email.content_subtype = 'html'  # To send HTML content
            email.send()


        request.session["user_id"] = str(user["_id"])
        request.session["user_email"] = user["Email"]

        userid = str(user["_id"])
        device_info = get_device_info(request)
        device_type, browser, os = device_info.split("&")

        if not user_sessions.find_one({
            "UserId" : userid,
            "Network_ip" : get_client_ip(request),
            "Device_Type" : device_type,
            "Browser" : browser,
            "OS" : os,
        }):
            user_sessions.insert_one({
                "UserId" : userid,
                "Network_ip" : get_client_ip(request),
                "Device_Type" : device_type,
                "Browser" : browser,
                "OS" : os,
                "Log_Time" : datetime.now()
            })
        else:
            user_sessions.update_one({
                "UserId" : userid,
                "Network_ip" : get_client_ip(request),
                "Device_Type" : device_type,
                "Browser" : browser,
                "OS" : os,},
                {"$set" : {"Log_Time" : datetime.now()
            }})

        redirect_url = request.session.get("url")
        if redirect_url:
            return redirect(redirect_url)
        return redirect("/Dashboard/Home/" + str(user["_id"]) + "/")

    except Exception as e:
        print(f"Google auth error: {str(e)}")
        return redirect("/Auth/Login/")
