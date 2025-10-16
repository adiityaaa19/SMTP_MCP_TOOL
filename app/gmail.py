import os
import requests
from fastmcp import FastMCP
from dotenv import load_dotenv

# Load env only if not in Docker/production
if os.getenv("ENV") != "production":
    load_dotenv()

# Initialize MCP server
mcp = FastMCP("Email Agent 📧")


def send_email_via_brevo(to_email: str, subject: str, body: str, from_email: str = None, 
                          message_id: str = None, references: str = None) -> dict:
    """
    Send email using Brevo REST API
    Args:
        message_id: Optional Message-ID to reply to (for threading)
        references: Optional References header (for threading)
    """
    try:
        # Read environment variables
        api_key = os.getenv("BREVO_API_KEY")
        smtp_from_email = os.getenv("SMTP_FROM_EMAIL")

        if not api_key:
            return {"success": False, "message": "BREVO_API_KEY not found in environment variables"}

        if not from_email:
            from_email = smtp_from_email

        # Build email payload
        html_body = body.replace("\n", "<br>")
        
        payload = {
            "sender": {"email": from_email},
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": f"<html><body>{html_body}</body></html>",
            "textContent": body
        }
        
        # Add threading headers if this is a reply
        if message_id:
            headers = {
                "In-Reply-To": message_id
            }
            if references:
                headers["References"] = f"{references} {message_id}"
            else:
                headers["References"] = message_id
            
            payload["headers"] = headers

        # Send email via Brevo API
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "api-key": api_key
            },
            json=payload
        )

        if response.status_code in [200, 201]:
            result = response.json()
            return {
                "success": True, 
                "message": f"Email sent successfully to {to_email}",
                "message_id": result.get("messageId", "N/A")
            }
        else:
            return {
                "success": False, 
                "message": f"Failed to send email: {response.status_code} - {response.text}"
            }

    except Exception as e:
        return {"success": False, "message": f"Failed to send email: {str(e)}"}


@mcp.tool()
def send_email_only(to_email: str, subject: str, body: str, from_email: str = None) -> str:
    """
    MCP tool endpoint to send an email.
    """
    result = send_email_via_brevo(to_email, subject, body, from_email)
    if result["success"]:
        return f"✅ {result['message']}\n📧 Message-ID: {result.get('message_id', 'N/A')}"
    return f"❌ {result['message']}"


@mcp.tool()
def reply_to_email(to_email: str, subject: str, body: str, message_id: str, 
                   references: str = None, from_email: str = None) -> str:
    """
    MCP tool to reply to an existing email thread.
    
    Args:
        to_email: Recipient email address
        subject: Email subject (typically starts with 'Re: ')
        body: Email body content
        message_id: The Message-ID of the email you're replying to
        references: Optional chain of Message-IDs from the thread (space-separated)
        from_email: Optional sender email (defaults to SMTP_FROM_EMAIL)
    """
    result = send_email_via_brevo(to_email, subject, body, from_email, message_id, references)
    if result["success"]:
        return f"✅ Reply sent successfully to {to_email}\n📧 Message-ID: {result.get('message_id', 'N/A')}"
    return f"❌ {result['message']}"


def send_sms_via_brevo(recipient: str, content: str, sender: str = None, 
                       sms_type: str = "transactional", unicode_enabled: bool = False) -> dict:
    """
    Send SMS using Brevo REST API
    Args:
        recipient: Phone number with country code (e.g., "33680065433" or "+33680065433")
        content: SMS message content
        sender: Sender name (alphanumeric, max 11 chars) or phone number
        sms_type: "transactional" or "marketing" (use marketing if content has opt-out)
        unicode_enabled: Enable unicode for special characters
    """
    try:
        # Read environment variables
        api_key = os.getenv("BREVO_API_KEY")

        if not api_key:
            return {"success": False, "message": "BREVO_API_KEY not found in environment variables"}

        # Build SMS payload
        payload = {
            "sender": sender,
            "recipient": recipient,
            "content": content,
            "type": sms_type,
            "unicodeEnabled": unicode_enabled
        }

        # Send SMS via Brevo API
        response = requests.post(
            "https://api.brevo.com/v3/transactionalSMS/send",
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "api-key": api_key
            },
            json=payload
        )

        if response.status_code in [200, 201]:
            result = response.json()
            return {
                "success": True, 
                "message": f"SMS sent successfully to {recipient}",
                "message_id": result.get("messageId", "N/A")
            }
        else:
            return {
                "success": False, 
                "message": f"Failed to send SMS: {response.status_code} - {response.text}"
            }

    except Exception as e:
        return {"success": False, "message": f"Failed to send SMS: {str(e)}"}


@mcp.tool()
def send_sms(recipient: str, content: str, sender: str = None, unicode_enabled: bool = False) -> str:
    """
    MCP tool to send a transactional SMS.
    
    Args:
        recipient: Phone number with country code (e.g., "33680065433" or "+1234567890")
        content: SMS message content
        sender: Optional sender name (alphanumeric, max 11 chars) or phone number
        unicode_enabled: Enable unicode for special characters (default: False)
    """
    result = send_sms_via_brevo(recipient, content, sender, "transactional", unicode_enabled)
    if result["success"]:
        return f"✅ {result['message']}\n📱 Message-ID: {result.get('message_id', 'N/A')}"
    return f"❌ {result['message']}"


def send_whatsapp_via_brevo(contact_numbers: list, sender_number: str, 
                             template_id: int = None, text: str = None) -> dict:
    """
    Send WhatsApp message using Brevo REST API
    Args:
        contact_numbers: List of phone numbers with country code (e.g., ["4915778559164"])
        sender_number: Your WhatsApp Business number (e.g., "917878172050")
        template_id: Template ID (required for first message to a contact)
        text: Message text (can be used after first template message)
    """
    try:
        # Read environment variables
        api_key = os.getenv("BREVO_API_KEY")

        if not api_key:
            return {"success": False, "message": "BREVO_API_KEY not found in environment variables"}

        if not template_id and not text:
            return {"success": False, "message": "Either template_id or text must be provided"}

        # Build WhatsApp payload
        payload = {
            "contactNumbers": contact_numbers,
            "senderNumber": sender_number
        }
        
        if template_id:
            payload["templateId"] = template_id
        if text:
            payload["text"] = text

        # Send WhatsApp message via Brevo API
        response = requests.post(
            "https://api.brevo.com/v3/whatsapp/sendMessage",
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "api-key": api_key
            },
            json=payload
        )

        if response.status_code in [200, 201]:
            result = response.json()
            return {
                "success": True, 
                "message": f"WhatsApp message sent successfully to {', '.join(contact_numbers)}",
                "response": result
            }
        else:
            return {
                "success": False, 
                "message": f"Failed to send WhatsApp: {response.status_code} - {response.text}"
            }

    except Exception as e:
        return {"success": False, "message": f"Failed to send WhatsApp: {str(e)}"}


@mcp.tool()
def send_whatsapp(contact_numbers: str, sender_number: str, 
                  template_id: int = None, text: str = None) -> str:
    """
    MCP tool to send a WhatsApp message.
    
    Args:
        contact_numbers: Phone number(s) with country code, comma-separated (e.g., "4915778559164" or "123,456")
        sender_number: Your WhatsApp Business number (e.g., "917878172050")
        template_id: Template ID for first message (required for new contacts)
        text: Message text (can be used after first template message)
    
    Note: The first message to a contact MUST use a template_id. 
          Create templates in Brevo dashboard: Campaigns > WhatsApp
    """
    # Convert comma-separated string to list
    numbers_list = [num.strip() for num in contact_numbers.split(",")]
    
    result = send_whatsapp_via_brevo(numbers_list, sender_number, template_id, text)
    if result["success"]:
        return f"✅ {result['message']}"
    return f"❌ {result['message']}"


def schedule_email_via_brevo(to_email: str, subject: str, body: str, scheduled_at: str,
                              from_email: str = None, batch_id: str = None) -> dict:
    """
    Schedule an email to be sent later using Brevo REST API
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body content
        scheduled_at: ISO 8601 datetime (e.g., "2024-10-16T15:30:00+05:30")
        from_email: Optional sender email
        batch_id: Optional batch ID to group multiple scheduled emails
    Note: Can schedule up to 72 hours in the future
    """
    try:
        # Read environment variables
        api_key = os.getenv("BREVO_API_KEY")
        smtp_from_email = os.getenv("SMTP_FROM_EMAIL")

        if not api_key:
            return {"success": False, "message": "BREVO_API_KEY not found in environment variables"}

        if not from_email:
            from_email = smtp_from_email

        # Build email payload with scheduling
        html_body = body.replace("\n", "<br>")
        
        payload = {
            "sender": {"email": from_email},
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": f"<html><body>{html_body}</body></html>",
            "textContent": body,
            "scheduledAt": scheduled_at
        }
        
        # Add batch ID if provided
        if batch_id:
            payload["batchId"] = batch_id

        # Schedule email via Brevo API
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "api-key": api_key
            },
            json=payload
        )

        if response.status_code in [200, 201]:
            result = response.json()
            return {
                "success": True, 
                "message": f"Email scheduled successfully for {to_email} at {scheduled_at}",
                "message_id": result.get("messageId", "N/A"),
                "batch_id": batch_id if batch_id else "N/A"
            }
        else:
            return {
                "success": False, 
                "message": f"Failed to schedule email: {response.status_code} - {response.text}"
            }

    except Exception as e:
        return {"success": False, "message": f"Failed to schedule email: {str(e)}"}


def delete_scheduled_email_via_brevo(identifier: str) -> dict:
    """
    Delete scheduled email using Brevo REST API
    Args:
        identifier: batchId or messageId of the scheduled email to delete
    """
    try:
        # Read environment variables
        api_key = os.getenv("BREVO_API_KEY")

        if not api_key:
            return {"success": False, "message": "BREVO_API_KEY not found in environment variables"}

        # Delete scheduled email via Brevo API
        response = requests.delete(
            f"https://api.brevo.com/v3/smtp/email/{identifier}",
            headers={
                "accept": "application/json",
                "api-key": api_key
            }
        )

        if response.status_code in [200, 204]:
            return {
                "success": True, 
                "message": f"Scheduled email(s) with identifier '{identifier}' deleted successfully"
            }
        else:
            return {
                "success": False, 
                "message": f"Failed to delete scheduled email: {response.status_code} - {response.text}"
            }

    except Exception as e:
        return {"success": False, "message": f"Failed to delete scheduled email: {str(e)}"}


@mcp.tool()
def schedule_email(to_email: str, subject: str, body: str, scheduled_at: str,
                   from_email: str = None, batch_id: str = None) -> str:
    """
    MCP tool to schedule an email to be sent at a specific time.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body content
        scheduled_at: When to send (ISO 8601 format, e.g., "2024-10-16T15:30:00+05:30")
        from_email: Optional sender email (defaults to SMTP_FROM_EMAIL)
        batch_id: Optional batch ID to group multiple scheduled emails (e.g., UUID)
    
    Note: Can schedule up to 72 hours in the future.
          Use the returned messageId or batchId to cancel if needed.
    """
    result = schedule_email_via_brevo(to_email, subject, body, scheduled_at, from_email, batch_id)
    if result["success"]:
        return f"✅ {result['message']}\n📧 Message-ID: {result.get('message_id', 'N/A')}\n📦 Batch-ID: {result.get('batch_id', 'N/A')}"
    return f"❌ {result['message']}"


@mcp.tool()
def delete_scheduled_email(identifier: str) -> str:
    """
    MCP tool to delete scheduled email(s).
    
    Args:
        identifier: batchId or messageId of the scheduled email to delete
    
    Note: This only works for SCHEDULED emails (emails set to be sent in the future).
          Already sent emails cannot be deleted.
    """
    result = delete_scheduled_email_via_brevo(identifier)
    if result["success"]:
        return f"✅ {result['message']}"
    return f"❌ {result['message']}"


if __name__ == "__main__":
    print("🚀 Starting Email, SMS & WhatsApp Agent MCP Server...")
    print("📧 Email: Sending via Brevo REST API with Threading Support")
    print("📱 SMS: Transactional SMS via Brevo REST API")
    print("💬 WhatsApp: Business messaging via Brevo REST API")
    mcp.run(transport="http", host="0.0.0.0", port=8000, path="/mcp")


