from flask import Blueprint, render_template,redirect,url_for, request, flash
from auth.forms import LoginForm, RegistrationForm
from auth.model import User, db
from course.model import Course
from emails.models import EmailTemplate
from emails.forms import Emailstemplate
from course.forms import Customizeform
from user.forms import Generateform,OpenAiform, CourseForm
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from openai import OpenAI

courses = Blueprint('courses', __name__)
def retrieve_email_template_from_database(template_id):
    # Query the database to retrieve the email template by ID
    email_template = EmailTemplate.query.filter_by(id=template_id).first()
    return email_template

def send_email(recipient, subject, body):
    # Configure SMTP server settings
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'harmonymwirigi99@gmail.com'
    sender_password = 'dcqw whew eoyq gyki'

    # Create a MIME multipart message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient
    message['Subject'] = subject

    # Define the HTML content of the email
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                color: #333;
                padding: 20px;
            }}
            .email-container {{
                background-color: #ffffff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }}
            .body {{
                font-size: 16px;
                line-height: 1.5;
                
            }}
            .footer {{
                font-size: 14px;
                color: #777;
                height: 60px;
                text-align: center;
                background-color: black;
            }}
            .footer-content{{
                padding-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                Animal news of Dogs 
            </div>
            <img src="/static/images/periodico.png" height="100px" width="90px">
            <br>
            <br>
            <div class="body">
            {body}
            <div class="footer">
                
                <p class="footer-content">&copy; 2024 Your Company. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Attach the email body as HTML
    message.attach(MIMEText(html_content, 'html'))

    # Connect to the SMTP server and send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)



@courses.route('/<course>', methods=['GET', 'POST'])
@login_required
def dashboard(course):
    customizeform = Customizeform()
    tempform = Generateform()
    form = Emailstemplate()
    keyform = OpenAiform()
    compainform = CourseForm()
    email = current_user.email
    
    
    
    if form.validate_on_submit():
        # This block will execute when the form is submitted and all fields pass validation
        # Access form data using form.field_name.data
        header = form.Header.data
        body = form.body.data
        footer = form.footer.data
        
        # Create a new EmailTemplate instance
        email_template = EmailTemplate(header=header, body=body, footer=footer, owner_id = current_user.id, compaign = course)
        # Add the new EmailTemplate instance to the database session
        db.session.add(email_template)
        # Commit the changes to the database
        db.session.commit()
       
        return redirect(url_for('courses.dashboard', compaign = course))  # Redirect to the dashboard to clear the form
    else:
        # Handle form validation failure as before
        pass
    
    email_templates = EmailTemplate.query.filter_by(owner_id=current_user.id, compaign=course).all()
    courses = Course.query.filter_by(owner_id=current_user.id).all()
    this_campaign = Course.query.filter_by(id=course).first()
    check_key = this_campaign.stripe_api_key
    if this_campaign.color:
        color = this_campaign.color
    else:
        color = "#fffff"
    code = this_campaign.url
    compaign_id = course
    db.session.commit() 
    
    
    return render_template('compaigndashboard.html', 
                           formu=form, 
                           email_templates=email_templates, 
                           tempform=tempform, 
                           email=email, 
                           keyform=keyform, 
                           compainform=compainform, 
                           courses=courses, 
                           compaign_id=compaign_id,
                           customizeform = customizeform, 
                           check_key=check_key,
                           url = code,
                           color = color,
                           active_compaign_id=int(course))  # Pass active_compaign_id to the template



@courses.route('/customize/<campaign>', methods =['POST', 'GET'])
def customize(campaign):
    customizeform = Customizeform()
    if customizeform.validate_on_submit():
        title = customizeform.title.data
        color = customizeform.color.data
        price = customizeform.price.data
        link = customizeform.link.data
        customize = Course.query.filter_by(id=campaign).first()
        customize.title  = title
        customize.color = color
        customize.price = price
        customize.courselink = link
        db.session.commit()
        return redirect(url_for('courses.dashboard',course = campaign))


@courses.route('/<id>/users')
@login_required
def users(id):
    customizeform = Customizeform()
    form = Emailstemplate()
    keyform=OpenAiform()
    compainform = CourseForm()
    compaign_id =id
    users =  User.query.filter_by(course_id = id).all()
    this_campaign = Course.query.filter_by(id=id).first()
    courses = Course.query.filter_by(owner_id=current_user.id).all()
    code = this_campaign.url
    if this_campaign.color:
        color = this_campaign.color
    else:
        color = "#fffff"
    check_key = this_campaign.stripe_api_key
    return render_template('compaignusers.html',
                           active_compaign_id=int(id),
                           url = code, 
                           users = users,
                           compaign_id=compaign_id,
                           check_key =check_key,
                           courses=courses,
                           customizeform = customizeform,
                           formu = form,keyform=keyform,
                           color = color,
                           compainform = compainform)

@courses.route('/config/<id>', methods=['POST'])
@login_required
def config(id):
    form = OpenAiform()
    if form.validate_on_submit():
        key = form.key.data
        compain = Course.query.filter_by(id = id).first()
        compain.stripe_api_key = key
        db.session.commit()  # Save the changes to t
        return redirect(url_for('courses.dashboard', course = id))

# dcqw whew eoyq gyki
@courses.route('/generate_email_body/<compaign>', methods=['POST'])
@login_required
def generate_email_body(compaign):
    # Retrieve template ID from request (assuming it's sent via POST)
    template_id = int(request.form.get('template_id'))  # Convert to integer
    compain = Course.query.filter_by(id = compaign).first()
    # Provide your OpenAI API key here
    api_key = compain.open_api_key

    client = OpenAI(api_key=api_key)

    # Fetch email template from your database based on the template ID
    # Replace this with your actual database retrieval logic
    email_template = retrieve_email_template_from_database(template_id)
    # Construct prompt for OpenAI API instructing to generate an email with specific parts
    prompt = f"Generate an email with the following parts:\n\nHeader: {email_template.header}\n\nBody: {email_template.body}\n\nFooter: {email_template.footer}"
    completion = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens = 2400,
            temperature = 1
        )
    response_text = completion.choices[0].text

    
   # Fetch users from the database whose status is 2
    users = User.query.filter_by(status=1).all()

    # Send the generated email to each user
    for user in users:
        send_email(user.email, email_template.header, response_text)

    # Flash a success message
    flash("Emails sent successfully", "success")

    # Redirect to the dashboard
    return redirect(url_for('users.dashboard'))

    
 
