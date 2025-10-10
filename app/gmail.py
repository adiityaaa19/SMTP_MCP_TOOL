# # server.py
# import os
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from fastmcp import FastMCP
# from dotenv import load_dotenv

# # Load environment variables from .env
# load_dotenv()

# # Initialize MCP server
# mcp = FastMCP("Email Agent 📧")


# def send_email_via_brevo(to_email: str, subject: str, body: str, from_email: str = None) -> dict:
#     """
#     Send email using Brevo SMTP
#     Args:
#         to_email: Recipient email address
#         subject: Email subject
#         body: Email body content
#         from_email: Sender email address (optional)
#     Returns:
#         Dictionary with status and message
#     """
#     try:
#         # Get SMTP credentials from environment
#         smtp_server = os.getenv("SMTP_SERVER", "smtp-relay.brevo.com")
#         smtp_port = int(os.getenv("SMTP_PORT", "587"))
#         smtp_login = os.getenv("SMTP_LOGIN")
#         smtp_password = os.getenv("SMTP_PASSWORD")
#         smtp_from_email = os.getenv("SMTP_FROM_EMAIL")
        
#         if not smtp_login or not smtp_password:
#             return {"success": False, "message": "SMTP credentials not found in .env file"}
        
#         # Use SMTP_FROM_EMAIL if from_email not provided
#         if not from_email:
#             from_email = smtp_from_email
        
#         # Create email message
#         msg = MIMEMultipart("alternative")
#         msg["Subject"] = subject
#         msg["From"] = from_email
#         msg["To"] = to_email
        
#         # Attach plain text and HTML versions
#         text_part = MIMEText(body, "plain")
#         html_body = body.replace("\n", "<br>")
#         html_part = MIMEText(f"<html><body>{html_body}</body></html>", "html")
#         msg.attach(text_part)
#         msg.attach(html_part)
        
#         # Connect and send email
#         with smtplib.SMTP(smtp_server, smtp_port) as server:
#             server.starttls()
#             server.login(smtp_login, smtp_password)
#             server.send_message(msg)
        
#         return {"success": True, "message": f"Email sent successfully to {to_email}"}
    
#     except Exception as e:
#         return {"success": False, "message": f"Failed to send email: {str(e)}"}


# @mcp.tool()
# def send_email_only(
#     to_email: str,
#     subject: str,
#     body: str,
#     from_email: str = None
# ) -> str:
#     """
#     MCP tool to send emails directly with provided content
#     """
#     result = send_email_via_brevo(to_email, subject, body, from_email)
    
#     if result["success"]:
#         return f"✅ {result['message']}"
#     else:
#         return f"❌ {result['message']}"


# if __name__ == "__main__":
#     print("🚀 Starting Email Agent MCP Server...")
#     print("📧 Features: Direct SMTP Email Sending (no AI)")
#     print("🔗 Server URL: http://127.0.0.1:8000/mcp")
#     mcp.run(transport="http", host="0.0.0.0", port=8000, path="/mcp")










import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastmcp import FastMCP
from dotenv import load_dotenv

# Load env only if not in Docker/production
if os.getenv("ENV") != "production":
    load_dotenv()

# Initialize MCP server
mcp = FastMCP("Email Agent 📧")


def send_email_via_brevo(to_email: str, subject: str, body: str, from_email: str = None) -> dict:
    """
    Send email using Brevo SMTP
    """
    try:
        # Read environment variables
        smtp_server = os.getenv("SMTP_SERVER", "smtp-relay.brevo.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_login = os.getenv("SMTP_LOGIN")
        smtp_password = os.getenv("SMTP_PASSWORD")
        smtp_from_email = os.getenv("SMTP_FROM_EMAIL")

        if not smtp_login or not smtp_password:
            return {"success": False, "message": "SMTP credentials not found in environment variables"}

        if not from_email:
            from_email = smtp_from_email

        # Build email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email

        text_part = MIMEText(body, "plain")

        # ✅ Fix: handle newlines separately before f-string
        html_body = body.replace("\n", "<br>")
        html_part = MIMEText(f"<html><body>{html_body}</body></html>", "html")

        msg.attach(text_part)
        msg.attach(html_part)

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_login, smtp_password)
            server.send_message(msg)

        return {"success": True, "message": f"Email sent successfully to {to_email}"}

    except Exception as e:
        return {"success": False, "message": f"Failed to send email: {str(e)}"}


@mcp.tool()
def send_email_only(to_email: str, subject: str, body: str, from_email: str = None) -> str:
    """
    MCP tool endpoint to send an email.
    """
    result = send_email_via_brevo(to_email, subject, body, from_email)
    if result["success"]:
        return f"✅ {result['message']}"
    return f"❌ {result['message']}"


if __name__ == "__main__":
    print("🚀 Starting Email Agent MCP Server...")
    print("📧 Features: Direct SMTP Email Sending via Docker environment variables")
    mcp.run(transport="http", host="0.0.0.0", port=8000, path="/mcp")


