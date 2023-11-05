import yagmail


sender_email = "im.adeliiman@gmail.com"
# receiver_emails = [RECEIVER_EMAIL_1, RECEIVER_EMAIL_2, RECEIVER_EMAIL_3]
receiver_emails = ["SHA16x16@gmail.com", ]
subject = "From Bot"
sender_password = "vorupluwfmcyzhpn"


def send_gmail(file):
    try: 
        yag = yagmail.SMTP(user=sender_email, password=sender_password)
        contents = [file,]
        yag.send(receiver_emails, subject, contents)
        print("email sending ... ... ...")

    except Exception as e:
        print(f'Something went wrong!\e{e}')