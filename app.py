from flask import Flask, render_template, request, redirect, url_for, session, flash
import os, json, smtplib, requests, urllib.parse
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "crm_portal_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "enquiries.json")

CUSTOMER_USERS = {
    "customer@demo.com": "1234",
    "user@demo.com": "1234"
}

ADMIN_USER = {
    "email": "admin@company.com",
    "password": "1234"
}

SERVICES = [
    "Digital Marketing",
    "Gen AI",
    "Data Analytics",
    "Advanced Artificial Intelligence"
]

COURSE_DETAILS = {
    "Digital Marketing": {
        "duration": "12 Weeks",
        "syllabus": [
            "Introduction to Digital Marketing",
            "Search Engine Optimization (SEO)",
            "Social Media Marketing",
            "Content Strategy & SEO Content Writing",
            "Google Ads & PPC Management",
            "Email Marketing Automation",
            "Marketing Analytics & Reporting"
        ],
        "benefits": "Gain hand-on experience with industry tools and work on real-time projects."
    },
    "Gen AI": {
        "duration": "8 Weeks",
        "syllabus": [
            "Fundamentals of Generative AI",
            "Large Language Models (LLMs) & Transformers",
            "Prompt Engineering Best Practices",
            "Working with OpenAI, Anthropic, and Google Gemini APIs",
            "RAG (Retrieval-Augmented Generation) Architecture",
            "AI Agent Frameworks (LangChain, AutoGPT)",
            "Ethical AI & Deployment Strategies"
        ],
        "benefits": "Build and deploy custom AI solutions for business automation."
    },
    "Data Analytics": {
        "duration": "10 Weeks",
        "syllabus": [
            "Introduction to Data Science & Analytics",
            "Excel for Data Analysis",
            "SQL for Database Querying",
            "Python for Data Manipulation (Pandas, Numpy)",
            "Data Visualization with PowerBI/Tableau",
            "Exploratory Data Analysis (EDA)",
            "Statistical Methods for Business Decisions"
        ],
        "benefits": "Master the art of storytelling with data and drive business insights."
    },
    "Advanced Artificial Intelligence": {
        "duration": "16 Weeks",
        "syllabus": [
            "Machine Learning Algorithms & Frameworks",
            "Deep Learning & Neural Networks",
            "Computer Vision & Image Processing",
            "Natural Language Processing (NLP)",
            "Reinforcement Learning Fundamentals",
            "AI System Design & Scalability",
            "Capstone Project: End-to-End AI Solution"
        ],
        "benefits": "Deep dive into the core of AI and build complex, intelligent systems."
    }
}

def load_enquiries():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_enquiries(enquiries):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(enquiries, f, indent=4)

def chatbot_response(message):
    msg = message.lower()
    if "price" in msg or "fee" in msg or "cost" in msg:
        return "Pricing depends on the selected service. Please submit an enquiry for complete pricing details."
    if "demo" in msg:
        return "A demo can be arranged after your enquiry submission. Our team will contact you soon."
    if "digital marketing" in msg or "marketing" in msg:
        return "We provide Digital Marketing solutions for branding, lead generation, and online growth."
    if "gen ai" in msg or "generative ai" in msg:
        return "Our Gen AI service includes AI tools, automation, chatbot support, and intelligent business solutions."
    if "data" in msg or "analytics" in msg:
        return "We provide Data Analytics services for reporting, insights, and business decision support."
    if "advanced artificial intelligence" in msg or "advanced ai" in msg:
        return "Advanced Artificial Intelligence is our premium service for intelligent automation and advanced AI solutions."
    if "hello" in msg or "hi" in msg:
        return "Hello! I can help you with services, pricing, demo requests, and support details."
    return "Thank you for your query. Please submit an enquiry and our team will get back to you shortly."

def send_course_email(user_name, user_email, service_name):
    # Reload environment variables to ensure we have the latest
    load_dotenv()
    
    # Get config from env and strip any accidental whitespace
    sender_email = (os.getenv("EMAIL_USER") or "").strip()
    sender_password = (os.getenv("EMAIL_PASS") or "").strip()
    
    if not sender_email or not sender_password:
        print(f"DEBUG: Email configuration missing! User: '{sender_email}', Pass provided? {'Yes' if sender_password else 'No'}")
        return False
    
    # Cast to string for type safety
    sender_email = str(sender_email)
    sender_password = str(sender_password)

    course = COURSE_DETAILS.get(service_name)
    if not course:
        return False

    # Create Message
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Course Details: {service_name} - AcceleratorX"
    message["From"] = sender_email
    message["To"] = user_email

    # Email HTML Template
    syllabus_html = "".join([f"<li>{item}</li>" for item in course['syllabus']])
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; border: 1px solid #eee; padding: 20px; border-radius: 10px;">
            <h2 style="color: #007bff;">Hello {user_name}!</h2>
            <p>Thank you for your interest in our <strong>{service_name}</strong> course.</p>
            <p>Here are the details you requested:</p>
            
            <div style="background: #f9f9f9; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0;">
                <p><strong>Duration:</strong> {course['duration']}</p>
                <p><strong>Proposed Syllabus:</strong></p>
                <ul>
                    {syllabus_html}
                </ul>
                <p><strong>Key Benefits:</strong> {course['benefits']}</p>
            </div>
            
            <p>Our team will reach out to you shortly for further discussion.</p>
            <p>Best Regards,<br><strong>AcceleratorX Team</strong></p>
        </div>
    </body>
    </html>
    """
    
    part = MIMEText(html, "html")
    message.attach(part)

    try:
        # Connect to Gmail SMTP (using port 465 for SSL or 587 for TLS)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, user_email, message.as_string())
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_telegram_notification(user_name, user_email, service_name):
    # Reload environment variables
    load_dotenv()
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("Telegram configuration is missing!")
        return False

    course = COURSE_DETAILS.get(service_name)
    if not course:
        return False

    # Create message text
    syllabus_str = "\n- ".join(course['syllabus'])
    message_text = (
        f"🚀 *New Course Enquiry!*\n\n"
        f"👤 *Name:* {user_name}\n"
        f"📧 *Email:* {user_email}\n"
        f"📚 *Course:* {service_name}\n\n"
        f"⏳ *Duration:* {course['duration']}\n"
        f"📝 *Syllabus Overview:* \n- {syllabus_str}\n\n"
        f"💡 *Benefits:* {course['benefits']}\n\n"
        f"✅ _Sending follow-up email..._"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return True
        else:
            print(f"Telegram API Error: {response.text}")
            return False
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")
        return False

@app.route("/")
def customer_login():
    return render_template("customer_login.html")

@app.route("/customer/login", methods=["POST"])
def customer_login_post():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    if email in CUSTOMER_USERS and CUSTOMER_USERS[email] == password:
        session["customer"] = email
        return redirect(url_for("customer_home"))
    flash("Invalid customer email or password.")
    return redirect(url_for("customer_login"))

@app.route("/customer/home")
def customer_home():
    if "customer" not in session:
        return redirect(url_for("customer_login"))
    return render_template("customer_home.html", customer_email=session["customer"], services=SERVICES)

@app.route("/submit_enquiry", methods=["POST"])
def submit_enquiry():
    if "customer" not in session:
        return redirect(url_for("customer_login"))
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    service = request.form.get("service", "").strip()
    message = request.form.get("message", "").strip()
    if not all([name, email, phone, service, message]):
        flash("All fields are required.")
        return redirect(url_for("customer_home"))
    enquiries = load_enquiries()
    enquiry = {
        "id": len(enquiries) + 1,
        "name": name,
        "email": email,
        "phone": phone,
        "service": service,
        "message": message,
        "status": "New",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "email_notification": f"Dear {name}, thank you for contacting us regarding {service}. Our team will contact you soon.",
        "whatsapp_message": f"Hi {name}, thanks for your enquiry about {service}. We will connect with you shortly."
    }
    enquiries.append(enquiry)
    save_enquiries(enquiries)
    
    # Generate Professional WhatsApp Message for the Admin to send to Customer
    course = COURSE_DETAILS.get(service, {})
    syllabus_summary = ", ".join(course.get('syllabus', [])[:3]) + "..."
    wa_text = (
        f"Hello {name}! 🚀\n\n"
        f"Thank you for your interest in our *{service}* course at AcceleratorX.\n\n"
        f"📍 *Course Overview:*\n"
        f"⏳ Duration: {course.get('duration')}\n"
        f"📚 Syllabus: {syllabus_summary}\n"
        f"💡 Benefits: {course.get('benefits')}\n\n"
        f"Would you like to schedule a free demo call? Let us know!"
    )
    # Clean phone numbers (must be digits only for wa.me)
    customer_phone_clean = "".join(filter(str.isdigit, phone))
    admin_wa_clean = "".join(filter(str.isdigit, os.getenv("ADMIN_WA_NUMBER", "")))

    # URL for Admin to send TO customer
    enquiry["admin_wa_url"] = f"https://wa.me/{customer_phone_clean}?text={urllib.parse.quote(wa_text)}"
    
    # URL for Customer to send TO admin
    enquiry["customer_wa_url"] = f"https://wa.me/{admin_wa_clean}?text={urllib.parse.quote(f'Hi! I just submitted an enquiry for the {service} course. I would like more details.')}"

    # Send Email Notification
    send_course_email(name, email, service)
    
    # Send Telegram Notification
    send_telegram_notification(name, email, service)

    flash(f"Enquiry submitted! Details have been sent to {email} and Telegram.")
    return render_template("thank_you.html", enquiry=enquiry)

@app.route("/chatbot", methods=["POST"])
def chatbot():
    message = request.form.get("message", "").strip()
    reply = chatbot_response(message) if message else "Please enter your query."
    return {"reply": reply}

@app.route("/customer/logout")
def customer_logout():
    session.pop("customer", None)
    return redirect(url_for("customer_login"))

@app.route("/admin/login")
def admin_login():
    return render_template("admin_login.html")

@app.route("/admin/login", methods=["POST"])
def admin_login_post():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    if email == ADMIN_USER["email"] and password == ADMIN_USER["password"]:
        session["admin"] = email
        return redirect(url_for("admin_dashboard"))
    flash("Invalid admin email or password.")
    return redirect(url_for("admin_login"))

@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for("admin_login"))
    enquiries = load_enquiries()
    service_count = {service: 0 for service in SERVICES}
    new_count = 0
    for enquiry in enquiries:
        if enquiry["service"] in service_count:
            service_count[enquiry["service"]] += 1
        if enquiry.get("status") == "New":
            new_count += 1
    return render_template(
        "admin_dashboard.html",
        enquiries=enquiries,
        total_enquiries=len(enquiries),
        new_count=new_count,
        service_count=service_count
    )

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))

if __name__ == "__main__":
    app.run(debug=True)
