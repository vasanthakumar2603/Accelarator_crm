import os, smtplib
from dotenv import load_dotenv

load_dotenv()

def test_email(recipient):
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")
    
    print(f"Testing with: {sender_email}")
    
    try:
        # Connect to Gmail SMTP (using port 465 for SSL)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            print("Login successful!")
            server.sendmail(sender_email, recipient, "Subject: Test\n\nTest email content.")
            print("Email sent successfully!")
            return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

if __name__ == "__main__":
    test_email("info.dheerandharanesh@gmail.com")
