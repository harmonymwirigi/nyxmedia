# auth.py
from flask import Blueprint, redirect,render_template,url_for,request, flash, abort,jsonify
from auth.forms import LoginForm, RegistrationForm
from werkzeug.security import generate_password_hash
from flask import render_template
from auth.model import User, db,Adminuser
from course.model import Course
import stripe
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import make_msgid
from flask import session
import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from flask_login import login_user, logout_user, login_required
# This is your Stripe CLI webhook secret for testing your endpoint locally.


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
    image_url = 'https://nyxmedia-tonirodriguez.pythonanywhere.com/static/images/nyx_logo.jpeg'
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
               nyxmedia/payments courses
            </div>
            <img src="{image_url}" alt="Logo" height="100" width="100">
            <br>
            <br>
            <div class="body">
            Es un placer saludarle, desde Nyx esperamos que disfrute de su compra, clique en el siguiente enlace para ver el contenido:
            <br>
            {body}
            <div class="footer">
                <p class="footer-content">&copy; 2024 nyxmedia/payments. All rights reserved.</p>
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


def create_customer(email, stripe_api_key):
    stripe.api_key = stripe_api_key
    customer = stripe.Customer.create(
        email=email
    )
    return customer.id

def create_default_price_and_update_product(product_id, unit_amount, key):
    try:
        # Initialize the Stripe API with your secret key
        stripe.api_key = key

        # Create a new price
        new_price = stripe.Price.create(
            product=product_id,
            unit_amount=unit_amount,  # Amount in cents
            currency="usd",
        )

        # Update the product's default price
        stripe.Product.modify(
            product_id,
            default_price=new_price.id
        )

        return new_price.id  # Return the ID of the created price
    except stripe.error.StripeError as e:
        print("Stripe Error:", e)
        return None
def create_checkout_session(course_id, created_price_id, customer, success_url, stripe_api_key, quantity=1):
    stripe.api_key = stripe_api_key
    try:
        session = stripe.checkout.Session.create(
            payment_intent_data={'metadata': {'course_id': course_id}},
            success_url=success_url,
            mode='payment',
            payment_method_types=['card'],
            customer=customer,
            line_items=[{
                'price': created_price_id,
                'quantity': quantity,
            }]
        )
        return session.url
    except Exception as e:
        print(f"Error creating Checkout Session: {e}")
        return None





def create_payment_intent(amount, currency, customer_id, course_id, stripe_api_key):
    stripe.api_key = stripe_api_key
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            customer=customer_id,
            metadata={'course_id': course_id}
        )
        return intent
    except Exception as e:
        print(f"Error creating Payment Intent: {e}")
        return None



# Define a Flask Blueprint named 'auth_bp'
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/webhook', methods=['POST'])
def handle_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    event = None

    try:
        # Parse the event first to extract metadata
        event = json.loads(payload)

        # Extract course_id from the event's metadata
        course_id = event['data']['object']['metadata']['course_id']

        # Retrieve the course and its endpoint secret
        course = Course.query.get(course_id)
        if not course:
            abort(404, description="Course not found")

        endpoint_secret = course.endpoint_secret

        # Verify the payload
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print(f"Invalid payload: {e}")
        abort(400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print(f"Invalid signature: {e}")
        abort(400)
    except KeyError as e:
        # Missing required metadata
        print(f"Missing metadata: {e}")
        abort(400)

    # Process the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)
    elif event['type'] == 'payment_intent.succeeded':
        session = event['data']['object']
        handle_payment_intent_succeeded(session)
    else:
        print(f"Unhandled event type {event['type']}")

    return '', 200



def handle_checkout_session(session):
    # Implement your logic to handle the checkout session
    print(f"Checkout session completed: {session}")
    # For example, update user status, send email, etc.

def handle_payment_intent_succeeded(payment_intent):
    # Extract necessary information from payment_intent
    payment_intent_id = payment_intent['id']
    customer = payment_intent['customer']
    amount = payment_intent['amount_received'] / 100  # Convert amount to dollars

    try:
        # Assuming you have a Payments model with appropriate fields
        payment = User.query.filter_by(customer_id=customer).first()
        course = Course.query.filter_by(id=payment.course_id).first()
        if payment:
            payment.payment_intent_id = payment_intent_id
            payment.amount = amount
            payment.status = 2  # Assuming '2' represents a successful payment status
            db.session.commit()
            send_email(payment.email, 'Course Subscription', course.courselink)
    except Exception as e:
        # Handle database update error
        print("Database update error:", e)





@auth_bp.route("/termsandconditions")
def termsandconditions():
    return render_template('terms_and_condition.html')

@auth_bp.route('/')
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Retrieve the user based on the provided email
        user = Adminuser.query.filter_by(email=form.email.data).first()
        if user:
            # Check if the password is correct
            # print(user.check_password(form.password.data))
            if user.password ==form.password.data:

                    login_user(user)

                    # If the user is an admin, redirect to the admin dashboard
                    return redirect(url_for('users.dashboard'))
                      # Replace 'admin.dashboard' with the appropriate endpoinT
            else:
                print('Incorrect password. Please try again.')
                flash('Incorrect password. Please try again.', 'danger')
        else:
            print('User does not exist. Please try again.')
            flash('User does not exist. Please try again.', 'danger')

    # Render the login template with the login form
    return render_template('login.html', form=form )

@auth_bp.route('/success')
def success():
    return render_template('success.html')

@auth_bp.route('/logout')
def logout():
    # Log out the user
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/register/<code>', methods=['GET', 'POST'])
def register(code):
    course = Course.query.filter_by(url=code).first()
    if not course:
        return redirect(url_for('auth.error', type=2))

    colo = course.color
    title = course.title
    price = course.price
    product = course.product_id
    key = course.stripe_api_key
    amount = int(round(price * 100))  # Ensure amount is an integer
    # link = course.courselink
    form = RegistrationForm()

    if form.validate_on_submit():
        # Check if the email is already registered in this campaign
        existing_user = User.query.filter_by(email=form.email.data, course_id=course.id).first()
        if existing_user:
            return redirect(url_for('auth.error', type=1))

        try:
            # Log steps to track progress
            print("Creating Stripe customer...")
            created_customer = create_customer(form.email.data, key)

            created_price_id = create_default_price_and_update_product(product, amount, key)

            # Create a Payment Intent


            # Define success and cancel URLs
            success_url = url_for('auth.success', _external=True)

            # Create a Checkout Session
            print("Creating Checkout Session...")
            checkout_session_url = create_checkout_session(course.id, created_price_id, created_customer, success_url, key, quantity=1)
            if not checkout_session_url:
                print("Failed to create Checkout Session")
                return redirect(url_for('auth.error', type=3))
            print(f"Created Checkout Session URL: {checkout_session_url}")

            # Add the new user to the database session
            print("Adding new user to the database...")
            new_user = User(
                email=form.email.data,
                customer_id=created_customer,
                amount=amount,
                status=1,
                course_id=course.id
            )
            db.session.add(new_user)
            db.session.commit()
            print("New user added to the database.")

            # Redirect to the checkout session URL after successful registration
            return redirect(checkout_session_url)
        except Exception as e:
            # Log the exception and handle it appropriately
            print(f"Error during registration: {e}")
            return redirect(url_for('auth.error', type=3))
    else:
        # Log form errors for debugging
        print("Form validation failed. Errors:", form.errors)

    # Render the registration form template
    return render_template('register.html', form=form, color=colo, title=title, code=code)







@auth_bp.route('/admin_register', methods=['GET', 'POST'])
def register_admin():
    form = RegistrationForm()
    if form.validate_on_submit():
        # hashed_password = generate_password_hash(form.password.data)
        new_admin = Adminuser(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        db.session.add(new_admin)
        db.session.commit()
        flash('Admin user created successfully!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('admin_register.html', form=form)

@auth_bp.route('/error/<type>')
def error(type):
    message = ""
    if type == '1':
        message  =  "Sorry , You are not allowed to register in the same compaign twice";
    if type == '2':
        message = "Sorry, the compaign does not exist"
    return render_template('404.html', message = message)

@auth_bp.route('/email')
def temp():
    return render_template("email_template.html")