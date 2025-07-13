from django.shortcuts import render,redirect
from bson import ObjectId
from datetime import datetime
from pymongo import DESCENDING
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import random
import pymongo




from django.conf import settings 
user_details = settings.MONGO_DB.userdata
user_records = settings.MONGO_DB.ExpenceRecords
user_sessions = settings.MONGO_DB.sessions
user_tickets = settings.MONGO_DB.Support





def dashboard(request,userid):
    if not request.session.get("user_id"):
        request.session["url"] = "/Dashboard/Home/" + userid + "/"
        return redirect("/Auth/Login/")
    
    if not user_details.find_one({"_id" : ObjectId(userid)}):
        request.session.flush()
        return redirect("/Home/")
    
    if not request.session.get("user_id") == userid:
        url = "/Dashboard/Home/" + request.session.get("user_id") + "/"
        return redirect(url)
    
    user = user_details.find_one({"_id" : ObjectId(userid)})
    try:
        if user["Name"] :
            name = user["Name"]
    
    except:
        usermail = user["Email"]
        name = ''
        for i in usermail:
            if (i != '@') :
                name +=i
            else:
                break
        
        user_details.update_one({"_id" : ObjectId(userid)},
                                {"$set" : {"Name" : name}})

    n = user_records.count_documents({"UserID": userid})
    user_records_cursor = user_records.find({"UserID": userid})

    total_due = 0
    savings = 0
    nonpaid_count = 0
    data_records = []
    for record in user_records_cursor:
        record["recid"] = str(record["_id"])  # Rename _id for template
        data_records.append(record)

        profit = (record["Spend_Amount"] - record["Orginal_Debited_Amount"])
        savings += profit

        if record["Status"] == "Non-Paid" :
            nonpaid_count += 1
            total_due += record["Due_Amount"]
        
    request.session["del_url"] = "/Dashboard/Home/" + userid + "/"
    request.session["edit_url"] = "/Dashboard/Home/" + userid + "/"

    context = {
        "id" : userid,
        "user" : name,
        "records" : data_records,
        "total" : n,
        "creationdate" : user["Creation_Time"],
        "category_count" : nonpaid_count,
        "total_due" : total_due,
        "total_saving" : savings
    }
    return render(request,"Account/dashboard.html",context)





# Add data Record 
def insert(request,userid):
    if not request.session.get("user_id"):
        request.session["url"] = "/Dashboard/Insert/Data/" + userid + "/"
        return redirect("/Auth/Login/")
    
    if not user_details.find_one({"_id" : ObjectId(userid)}):
        request.session.flush()
        return redirect("/Home/")
    
    if not request.session.get("user_id") == userid:
        url = "/Dashboard/Home/" + request.session.get("user_id") + "/"
        return redirect(url)
    
    user = user_details.find_one({"_id" : ObjectId(userid)})
    name = user["Name"]

    if request.method == "POST":
        date = datetime.strptime(request.POST.get("date"), "%Y-%m-%d")
        description = request.POST.get("description")
        spend_amount = float(request.POST.get("spend"))
        orginal_amount = float(request.POST.get("org"))
        due_from = request.POST.get("dueFrom")
        due_amount = float(request.POST.get("due"))
        status = request.POST.get("status")
        notes = request.POST.get("notes")

        user_records.insert_one({
            "UserID" : userid,
            "Date" : date,
            "Description" : description,
            "Spend_Amount" : spend_amount,
            "Orginal_Debited_Amount" : orginal_amount,
            "Due_From" : due_from,
            "Due_Amount" : due_amount,
            "Status" : status,
            "Notes" : notes,
            "Insertion_Time" : datetime.now(),
            "Last_Edited_Time" : datetime.now()
        })
        context = {
            "id" : userid,
            "user" : name,
            "msg" : "Data Stored Successfully."
        }
        return render(request,"Account/add_record.html",context)
    
    context = {
        "id" : userid,
        "user" : name
    }
    return render(request,"Account/add_record.html",context)







# View All Data
def view(request,userid):
    if not request.session.get("user_id"):
        request.session["url"] = "/Dashboard/View/Data/" + userid + "/"
        return redirect("/Auth/Login/")
    
    if not user_details.find_one({"_id" : ObjectId(userid)}):
        request.session.flush()
        return redirect("/Home/")
    
    if not request.session.get("user_id") == userid:
        url = "/Dashboard/Home/" + request.session.get("user_id") + "/"
        return redirect(url)
    
    user = user_details.find_one({"_id" : ObjectId(userid)})
    name = user["Name"]

    user_records_cursor = user_records.find({"UserID": userid})
    data_records = []
    for record in user_records_cursor:
        record["recid"] = str(record["_id"])  # Rename _id for template
        data_records.append(record)


    
    request.session["del_url"] = "/Dashboard/View/Data/" + userid + "/"
    request.session["edit_url"] = "/Dashboard/View/Data/" + userid + "/"
    context = {
        "id" : userid,
        "user" : name,
        "records" : data_records,
    }
    return render(request,"Account/view_records.html",context)






#delete Data
def delRecord(request, recordid, userid):
    if not request.session.get("user_id"):
        request.session["url"] = "/Dashboard/Home/" + userid + "/"
        return redirect("/Auth/Login/")
    
    if not request.session.get("user_id") == userid:
        url = "/Dashboard/Home/" + request.session.get("user_id") + "/"
        return redirect(url)

    if not user_details.find_one({"_id" : ObjectId(userid)}):
        request.session.flush()
        return redirect("/Home/")
    
    url = request.session.get("del_url")

    if not user_records.find_one({"_id" : ObjectId(recordid)}):
        return redirect(url)
    
    else:
        user_records.delete_one({"_id" : ObjectId(recordid)})
        return redirect(url)
    



# edit data records
def edit(request, recordid, userid):
    if not request.session.get("user_id"):
        request.session["url"] = "/Dashboard/Home/" + userid + "/"
        return redirect("/Auth/Login/")

    if not user_details.find_one({"_id" : ObjectId(userid)}):
        request.session.flush()
        return redirect("/Home/")
    
    if not request.session.get("user_id") == userid:
        url = "/Dashboard/Home/" + request.session.get("user_id") + "/"
        return redirect(url)

    url = request.session.get("edit_url")

    if not user_records.find_one({"_id" : ObjectId(recordid)}):
        return redirect(url)
    
    
    if request.method == "POST":
        date = datetime.strptime(request.POST.get("date"), "%Y-%m-%d")
        description = request.POST.get("description")
        spend_amount = float(request.POST.get("spend"))
        orginal_amount = float(request.POST.get("org"))
        due_from = request.POST.get("dueFrom")
        due_amount = float(request.POST.get("due"))
        status = request.POST.get("status")
        notes = request.POST.get("notes")   

        user_records.update_one( {"_id" : ObjectId(recordid)},
            {"$set" : {
            "UserID" : userid,
            "Date" : date,
            "Description" : description,
            "Spend_Amount" : spend_amount,
            "Orginal_Debited_Amount" : orginal_amount,
            "Due_From" : due_from,
            "Due_Amount" : due_amount,
            "Status" : status,
            "Notes" : notes,
            "Last_Edited_Time" : datetime.now()
        }})
        return redirect(url)  

    user = user_details.find_one({"_id" : ObjectId(userid)})
    name = user["Name"]

    data = user_records.find_one({"_id" : ObjectId(recordid)})
    dt = data["Date"]
    formatted_date = dt.strftime("%Y-%m-%d")

    path = request.session.get("edit_url")

    context = {
        "id" : userid,
        "user" : name,
        "details" : data,
        "date" : formatted_date,
        "path" : path
    }
    return render(request,"Account/edit_record.html", context)






def search(request,userid):
    if not request.session.get("user_id"):
        request.session["url"] = "/Dashboard/Filter/Data/" + userid + "/"
        return redirect("/Auth/Login/")

    if not user_details.find_one({"_id" : ObjectId(userid)}):
        request.session.flush()
        return redirect("/Home/")
    
    if not request.session.get("user_id") == userid:
        url = "/Dashboard/Home/" + request.session.get("user_id") + "/"
        return redirect(url)
    
    user = user_details.find_one({"_id" : ObjectId(userid)})
    name = user["Name"]

    if request.method == "GET": 
            date = request.GET.get("date","")
            due_from = request.GET.get("due_from","")
            reason = request.GET.get("description","")
            status = request.GET.get("status","")

            query = { "UserID" : userid }

            if date:
                query["Date"] = date
            if due_from:
                query["Due_From"] = due_from.strip()
            if reason:
                query["Description"] = reason.strip()
            if status:
                query["Status"] = status    


            user_records_cursor = user_records.find(query)
            data_records = []
            for record in user_records_cursor:
                record["recid"] = str(record["_id"])  # Rename _id for template
                data_records.append(record)


            request.session["del_url"] = "/Dashboard/Filter/Data/" + userid + "/?date=" + date +"&due_from=" + due_from + "&description=" + reason + "&status=" + status
            request.session["edit_url"] = "/Dashboard/Filter/Data/" + userid + "/?date=" + date +"&due_from=" + due_from + "&description=" + reason + "&status=" + status
            path = request.session.get("edit_url")

            context = {
                "id" : userid,
                "user" : name,
                "records" : data_records,
                "path" : path
            }
            return render(request,"Account/filter_records.html",context)
    
    request.session["del_url"] = "/Dashboard/Filter/Data/" + userid + "/?date=" + date +"&due_from=" + due_from + "&description=" + reason + "&status=" + status
    request.session["edit_url"] = "/Dashboard/Filter/Data/" + userid + "/?date=" + date +"&due_from=" + due_from + "&description=" + reason + "&status=" + status
    path = request.session.get("edit_url")

    context = {
        "id" : userid,
        "user" : name,
        "path" : path
    }
    return render(request,"Account/filter_records.html",context)




# modify record page
def modify(request,userid):
    if not request.session.get("user_id"):
        request.session["url"] = "/Dashboard/Modify/Data/" + userid + "/"
        return redirect("/Auth/Login/")

    if not user_details.find_one({"_id" : ObjectId(userid)}):
        request.session.flush()
        return redirect("/Home/")
    
    if not request.session.get("user_id") == userid:
        url = "/Dashboard/Home/" + request.session.get("user_id") + "/"
        return redirect(url)
    
    user = user_details.find_one({"_id" : ObjectId(userid)})
    name = user["Name"]

    if request.method == "GET": 
        date = request.GET.get("date","")
        due_from = request.GET.get("due_from","")
        reason = request.GET.get("description","")
        status = request.GET.get("status","")

        query = { "UserID" : userid }

        if date:
            query["Date"] = date
        if due_from:
            query["Due_From"] = due_from.strip()
        if reason:
            query["Description"] = reason.strip()
        if status:
            query["Status"] = status    


        user_records_cursor = user_records.find(query)
        data_records = []
        for record in user_records_cursor:
            record["recid"] = str(record["_id"])  # Rename _id for template
            data_records.append(record)


        
        request.session["edit_url"] = "/Dashboard/Modify/Data/" + userid + "/?date=" + date +"&due_from=" + due_from + "&description=" + reason + "&status=" + status
        path = request.session.get("edit_url")

        context = {
            "id" : userid,
            "user" : name,
            "records" : data_records,
            "path" : path
        }
        return render(request,"Account/modify_records.html",context)
    
    if request.method == "POST":
        sel_ids = request.POST.getlist("record_ids")
        action = request.POST.get("action")
        new_status = request.POST.get("new_status")


        if action == 'status' :
            for i in sel_ids:
                user_records.update_one({"_id" : ObjectId(i)},
                                        {"$set": {"Status" : new_status }})
        
        if action == 'delete' :
            for i in sel_ids:
                user_records.delete_one({"_id" : ObjectId(i)})

        path = request.session.get("edit_url")
        return redirect(path)
    
    context = {
        "id" : userid,
        "user" : name,
    }
    return render(request,"Account/modify_records.html",context)






# project settings
def setting(request,userid):
    if not request.session.get("user_id"):
        request.session["url"] = "/Dashboard/Settings/" + userid + "/"
        return redirect("/Auth/Login/")
    
    if not user_details.find_one({"_id" : ObjectId(userid)}):
        request.session.flush()
        return redirect("/Home/")
    
    if not request.session.get("user_id") == userid:
        url = "/Dashboard/Home/" + request.session.get("user_id") + "/"
        return redirect(url)
    
    if request.method == "POST":
        username = request.POST.get("username")
        mobile = request.POST.get("usernum")

        user_details.update_one({"_id" : ObjectId(userid)},
                                {"$set": {"Name" : username, "Mobile" : mobile}})
        uri = "/Dashboard/Settings/" + userid + "/"
        return redirect(uri)

    user = user_details.find_one({"_id" : ObjectId(userid)})
    name = user["Name"]

    session = user_sessions.find({"UserId": userid}).sort("Log_Time", DESCENDING).limit(2)
    all_sessions = user_sessions.find({"UserId": userid}).sort("Log_Time", DESCENDING)
    
    context = {
        "id" : userid,
        "user" : name,
        "userdetails" : user,
        "sessions" : session,
        "all_sessions" : all_sessions
    }
    return render(request,"Account/settings.html",context)


#Account Delete
def deluser(request,userid):
    if not request.session.get("user_id"):
        request.session["url"] = "/Dashboard/Settings/" + userid + "/"
        return redirect("/Auth/Login/")
    
    if not user_details.find_one({"_id" : ObjectId(userid)}):
        request.session.flush()
        return redirect("/Home/")
    
    if not request.session.get("user_id") == userid:
        url = "/Dashboard/Home/" + request.session.get("user_id") + "/"
        return redirect(url)
    
    user = user_details.find_one({"_id" : ObjectId(userid)})
    usermail = user["Email"]

    user_records.delete_many({"UserID" : userid})
    user_details.delete_one({"_id" : ObjectId(userid)})
    user_sessions.delete_many({"UserId" : userid})
    user_tickets.delete_many({"User_id": userid})

    value = {
        "domain" : request.build_absolute_uri('/')
        }
    subject = 'Your Spend Server account has been successfully deleted'
    html_message = render_to_string('Email_template/account_deletion_email_template.html',value)
    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email='spendserver@gmail.com',
        to=[usermail],
    )

    email.content_subtype = 'html'  # To send HTML content
    email.send()
    request.session.flush()
    return redirect("/Home/")
    




# Help page
def support(request,userid):
    if not request.session.get("user_id"):
        request.session["url"] = "/Dashboard/Support/" + userid + "/"
        return redirect("/Auth/Login/")
    
    if not user_details.find_one({"_id" : ObjectId(userid)}):
        request.session.flush()
        return redirect("/Home/")
    
    if not request.session.get("user_id") == userid:
        url = "/Dashboard/Home/" + request.session.get("user_id") + "/"
        return redirect(url)
    
    user = user_details.find_one({"_id" : ObjectId(userid)})
    name = user["Name"]

    is_Admin = False
    try:
        if user["Admin"] == True:
            is_Admin = True
    except:
        is_Admin = False
    
    context = {
        "id" : userid,
        "user" : name,
        "isAdmin" : is_Admin
    }
    return render(request,"Account/help.html",context)





# generate a unique ticket number
def genToken():
    temp = random.randint(100000,999999)
    if user_tickets.find_one({"Ticket_id" : temp}):
        return genToken()
    else:
        return temp
    

# coustomer care page
def ticket(request,userid):
    if not request.session.get("user_id"):
        request.session["url"] = "/Dashboard/Support/Ticket/" + userid + "/"
        return redirect("/Auth/Login/")
    
    if not user_details.find_one({"_id" : ObjectId(userid)}):
        request.session.flush()
        return redirect("/Home/")
    
    if not request.session.get("user_id") == userid:
        url = "/Dashboard/Home/" + request.session.get("user_id") + "/"
        return redirect(url)
    
    user = user_details.find_one({"_id" : ObjectId(userid)})
    name = user["Name"]

    
    try:
        if user["Admin"] == True:
            url = "/Dashboard/Support/Ticket/Admin/" + userid + "/"
            return redirect(url)
    except:
        url = "/Dashboard/Support/Ticket/" + userid + "/"
        return redirect(url)

    if request.method == "POST":
        sub = request.POST.get("subject")
        details = request.POST.get("details")

        messages = [{
            "Message" : details,
            "Sender_id" : userid,
            "Timestamp" : datetime.now(),
        }]
        temp = genToken()
        user_tickets.insert_one({
            "User_id" : userid,
            "Ticket_id" : temp,
            "Status" : "Open",
            "Subject" : sub.capitalize(),
            "Messages" : messages,
            "Ticket_Creation_Time" : datetime.now(),
        })

        #send email
        domain = request.build_absolute_uri('/')
        domain = domain + "/Dashboard/Support/Ticket/" + userid +"/"
        value = {
            "domain" : domain,
            "ticket_number" : temp,
            "ticket_subject" : sub.capitalize(),
            "ticket_created_time" : datetime.now(),
            "ticket_message" : details
            }
        
        subject = 'Support Ticket Created'
        html_message = render_to_string('Email_template/ticket_creation.html',value)
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email='spendserver@gmail.com',
            to=[user["Email"], 'spendserver@gmail.com'],
        )

        email.content_subtype = 'html'  # To send HTML content
        email.send()

        url = "/Dashboard/Support/Ticket/" + userid +"/"
        return redirect(url)


    user_ticket = user_tickets.find({"User_id": userid}).sort([
        ("Status", pymongo.DESCENDING),  # "Open" comes before "Closed"
        ("Ticket_Creation_Time", pymongo.DESCENDING)  # Newest first
    ])
    tickets = []
    for ticket in user_ticket:
        ticket["tid"] = str(ticket["_id"])  # Rename _id for template
        tickets.append(ticket)

    context = {
        "id" : userid,
        "user" : name,
        "tickets" : tickets
    }
    return render(request,"Account/support_ticket.html",context)






# admin page to manage all trickets
def admin(request,userid):
    if not request.session.get("user_id"):
        request.session["url"] = "/Dashboard/Support/Ticket/Admin/" + userid + "/"
        return redirect("/Auth/Login/")
    
    if not user_details.find_one({"_id" : ObjectId(userid)}):
        request.session.flush()
        return redirect("/Home/")

    if not request.session.get("user_id") == userid:
        url = "/Dashboard/Home/" + request.session.get("user_id") + "/"
        return redirect(url)
    
    try:
        if not user_details.find_one({ "Admin" : True}):
            url = "/Dashboard/Support/Ticket/" + userid + "/"
            return redirect(url)
    except:
        url = "/Dashboard/Support/Ticket/" + userid + "/"
        return redirect(url)    
    


    user = user_details.find_one({"_id" : ObjectId(userid)})
    name = user["Name"]
    user_ticket = user_tickets.find()

    tickets = []
    for ticket in user_ticket:
        ticket["tid"] = str(ticket["_id"])  # Rename _id for template

        temp_user = user_details.find_one({"_id" : ObjectId(ticket["User_id"]) }) 
        username = temp_user["Name"]
        ticket["username"] = username

        tickets.append(ticket)

    context = {
        "id" : userid,
        "user" : name,
        "tickets" : tickets
    }
    return render(request,"Account/admin_support.html",context)





# user Conversation Page
def chat(request, ticketid, userid):
    if not request.session.get("user_id"):
        request.session["url"] = "/Dashboard/Support/Ticket/" + ticketid + "/" +  userid + "/"
        return redirect("/Auth/Login/")

    if not user_details.find_one({"_id" : ObjectId(userid)}):
        request.session.flush()
        return redirect("/Home/")
    
    if not request.session.get("user_id") == userid:
        url = "/Dashboard/Home/" + request.session.get("user_id") + "/"
        return redirect(url)
    
    if not user_tickets.find_one({"_id" : ObjectId(ticketid)}):
        url = "/Dashboard/Support/Ticket/" + userid + "/"
        return redirect(url)
    
    user = user_details.find_one({"_id" : ObjectId(userid)})
    name = user["Name"]

    user_ticket = user_tickets.find_one({"_id" : ObjectId(ticketid)})

    if request.method == "POST" : 
        msg = request.POST.get("message")
        reopen = request.POST.get("reopen")

        if msg:
            messages = user_ticket["Messages"]
            messages.append({
                "Message" : msg,
                "Sender_id" : userid,
                "Timestamp" : datetime.now()
            })
            user_tickets.update_one(
                {"_id": ObjectId(ticketid)},
                {"$set": {"Messages": messages}}
            )
            url = "/Dashboard/Support/Ticket/" + ticketid + "/" + userid + "/"
            return redirect(url)
        
        if reopen:
            user_tickets.update_one(
                {"_id": ObjectId(ticketid)},
                {"$set": {"Status": "Open"}}
            )

            #send email
            domain = request.build_absolute_uri('/')
            domain = domain + "/Dashboard/Support/Ticket/" + ticketid + "/" + userid +"/"
            value = {
                "domain" : domain,
                "ticket_number" : user_ticket["Ticket_id"],
                "ticket_subject" : user_ticket["Subject"]
                }
            
            subject = 'Support Ticket Re-Opened'
            html_message = render_to_string('Email_template/ticket_reopen.html',value)
            email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email='spendserver@gmail.com',
                to=[ user["Email"], 'spendserver@gmail.com'],
            )

            email.content_subtype = 'html'  # To send HTML content
            email.send()


            url = "/Dashboard/Support/Ticket/" + ticketid + "/" + userid + "/"
            return redirect(url)

    context = {
        "id" : userid,
        "user" : name,
        "ticket" : user_ticket
    }
    return render(request,"Account/conversation.html",context)






# admin conversation page
def adminChat(request, ticketid, userid):
    if not request.session.get("user_id"):
        request.session["url"] = "/Dashboard/Support/Ticket/Admin/" + ticketid + "/" +  userid + "/"
        return redirect("/Auth/Login/")

    if not user_details.find_one({"_id" : ObjectId(userid)}):
        request.session.flush()
        return redirect("/Home/")

    if not request.session.get("user_id") == userid:
        url = "/Dashboard/Home/" + request.session.get("user_id") + "/"
        return redirect(url)
    
    if not user_tickets.find_one({"_id" : ObjectId(ticketid)}):
        url = "/Dashboard/Support/Ticket/" + userid + "/"
        return redirect(url)
    
    try:
        if not user_details.find_one({ "Admin" : True}):
            url = "/Dashboard/Support/Ticket/" + userid + "/"
            return redirect(url)
    except:
        url = "/Dashboard/Support/Ticket/" + userid + "/"
        return redirect(url)
    
    user_ticket = user_tickets.find_one({"_id" : ObjectId(ticketid)})
    user = user_details.find_one({"_id" : ObjectId(userid)})
    name = user["Name"]
    
    temp_user = user_details.find_one({"_id" : ObjectId(user_ticket["User_id"])})
    mail = temp_user["Email"]
    
    if request.method == "POST":
        close = request.POST.get("close")
        reopen = request.POST.get("reopen")
        message = request.POST.get("message")

        if close:
            user_tickets.update_one(
                {"_id" : ObjectId(ticketid)},
                {"$set":{
                    "Status" : "Closed",
                    "Ticket_Close_Time" : datetime.now()
                }},
                upsert=True
            )

            #send email
            domain = request.build_absolute_uri('/')
            domain = domain + "/Dashboard/Support/Ticket/" + ticketid + "/" + userid +"/"
            value = {
                "domain" : domain,
                "ticket_number" : user_ticket["Ticket_id"],
                "ticket_subject" : user_ticket["Subject"],
                }
            
            subject = 'Support Ticket Closed'
            html_message = render_to_string('Email_template/ticket_close.html',value)
            email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email='spendserver@gmail.com',
                to=[ mail, 'spendserver@gmail.com'],
            )

            email.content_subtype = 'html'  # To send HTML content
            email.send()

            url = "/Dashboard/Support/Ticket/Admin/" + ticketid + "/" +  userid + "/"
            return redirect(url)
        
        elif reopen:
            user_tickets.update_one(
                {"_id" : ObjectId(ticketid)},
                {"$set":{
                    "Status" : "Open",
                    "ticket_reopened_time" : datetime.now()
                }},
                upsert=True
            )

            #send email
            domain = request.build_absolute_uri('/')
            domain = domain + "/Dashboard/Support/Ticket/" + ticketid + "/" + userid +"/"
            value = {
                "domain" : domain,
                "ticket_number" : user_ticket["Ticket_id"],
                "ticket_subject" : user_ticket["Subject"],
                }
            
            subject = 'Support Ticket Re-Opened'
            html_message = render_to_string('Email_template/ticket_reopen.html',value)
            email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email='spendserver@gmail.com',
                to=[ mail, 'spendserver@gmail.com'],
            )

            email.content_subtype = 'html'  # To send HTML content
            email.send()

            url = "/Dashboard/Support/Ticket/Admin/" + ticketid + "/" +  userid + "/"
            return redirect(url)
        
        else : 
            msg = user_ticket["Messages"]
            msg.append({
                "Message" : message,
                "Sender_id" : userid,
                "Timestamp" : datetime.now()
            })
            user_tickets.update_one(
                {"_id": ObjectId(ticketid)},
                {"$set": {"Messages": msg}}
            )
            url = "/Dashboard/Support/Ticket/Admin/" + ticketid + "/" +  userid + "/"
            return redirect(url)


    uid = user_ticket["User_id"]
    coustomer = user_details.find_one({"_id" : ObjectId(uid)})

    context = {
        "id" : userid,
        "user" : name,
        "ticket" : user_ticket,
        "userdetails" : coustomer

    }
    return render(request,"Account/admin_chat.html",context)