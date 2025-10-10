# server.py
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastmcp import FastMCP
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("Email Agent 📧")

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_email_content(context: str, tone: str = "professional") -> str:
    """
    Generate email content using Groq LLM
    
    Args:
        context: The context or main points for the email
        tone: The tone of the email (professional, friendly, formal)
    
    Returns:
        Generated email content
    """
    try:
        prompt = f"""You are a professional email writer. Generate a well-structured email based on the following context.

Context: {context}

Tone: {tone}

Requirements:
- Write a complete, professional email
- Include appropriate greeting and closing
- Keep it concise and clear
- Make it engaging and actionable
- Do NOT include subject line (that will be provided separately)

Generate the email body only:"""

        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False
        )
        
        return completion.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Error generating email content: {str(e)}"


def send_email_via_brevo(to_email: str, subject: str, body: str, from_email: str = None) -> dict:
    """
    Send email using Brevo SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body content
        from_email: Sender email address (optional)
    
    Returns:
        Dictionary with status and message
    """
    try:
        # Get SMTP credentials from environment
        smtp_server = os.getenv("SMTP_SERVER", "smtp-relay.brevo.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_login = os.getenv("SMTP_LOGIN")
        smtp_password = os.getenv("SMTP_PASSWORD")
        smtp_from_email = os.getenv("SMTP_FROM_EMAIL")
        
        if not smtp_login or not smtp_password:
            return {
                "success": False,
                "message": "SMTP credentials not found in .env file"
            }
        
        # Use SMTP login as from_email if not provided
        if not from_email:
            from_email = smtp_from_email
        
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email
        
        # Add HTML and plain text parts
        text_part = MIMEText(body, "plain")
        html_body = body.replace("\n", "<br>")
        html_part = MIMEText(f"<html><body>{html_body}</body></html>", "html")
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Connect to SMTP server and send
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_login, smtp_password)
            server.send_message(msg)
        
        return {
            "success": True,
            "message": f"Email sent successfully to {to_email}"
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to send email: {str(e)}"
        }


@mcp.tool()
def send_ai_email(
    to_email: str,
    subject: str,
    context: str,
    tone: str = "professional",
    from_email: str = None
) -> str:
    """
    Generate and send an email using AI
    
    Args:
        to_email: Recipient's email address
        subject: Email subject line
        context: Context or key points for the email (AI will generate full content)
        tone: Tone of the email - options: professional, friendly, formal (default: professional)
        from_email: Sender's email address (optional, defaults to SMTP login)
    
    Returns:
        Status message with email details
    """
    # Generate email content using Groq LLM
    email_body = generate_email_content(context, tone)
    
    # Send email via Brevo
    result = send_email_via_brevo(to_email, subject, email_body, from_email)
    
    if result["success"]:
        return f"""✅ Email Sent Successfully!

To: {to_email}
Subject: {subject}

Generated Content:
{email_body}

Status: {result['message']}"""
    else:
        return f"""❌ Email Failed to Send

Error: {result['message']}

Generated Content (not sent):
{email_body}"""


@mcp.tool()
def send_direct_email(
    to_email: str,
    subject: str,
    body: str,
    from_email: str = None
) -> str:
    """
    Send an email directly without AI generation
    
    Args:
        to_email: Recipient's email address
        subject: Email subject line
        body: Complete email body content
        from_email: Sender's email address (optional, defaults to SMTP login)
    
    Returns:
        Status message
    """
    result = send_email_via_brevo(to_email, subject, body, from_email)
    
    if result["success"]:
        return f"✅ {result['message']}"
    else:
        return f"❌ {result['message']}"


if __name__ == "__main__":
    print("🚀 Starting Email Agent MCP Server...")
    print("📧 Features: AI Email Generation + SMTP Sending")
    print("🔗 Server URL: http://127.0.0.1:8000/mcp")
    mcp.run(transport="http", host="0.0.0.0", port=8000, path="/mcp")