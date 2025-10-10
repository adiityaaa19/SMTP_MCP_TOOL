# Gmail MCP Tool 📧

A Model Context Protocol (MCP) server that provides email sending capabilities through SMTP using Brevo (formerly Sendinblue) as the email service provider.

## Features

- 📧 **Direct Email Sending**: Send emails programmatically via SMTP
- 🔧 **MCP Integration**: Compatible with MCP-enabled AI assistants
- 🐳 **Docker Support**: Containerized deployment ready
- 🔒 **Environment-based Configuration**: Secure credential management
- 📝 **HTML & Plain Text**: Supports both email formats

## Project Structure

```
gmail_mcp_tool/
├── app/
│   ├── gmail.py           # Main MCP server implementation
│   └── requirements.txt   # Python dependencies
├── .env                   # Environment variables (local development)
├── dockerfile             # Docker configuration
├── Dockerfile.smtp        # Alternative Docker configuration
├── test.py               # Test script
└── README.md             # This file
```

## Prerequisites

- Python 3.11+
- Brevo SMTP account and credentials
- Docker (optional, for containerized deployment)

## Installation & Setup

### 1. Clone/Download the Project

```bash
git clone <repository-url>
cd gmail_mcp_tool
```

### 2. Environment Configuration

Create a `.env` file in the project root with your Brevo SMTP credentials:

```env
# Groq API Configuration (if needed for AI features)
GROQ_API_KEY="your_groq_api_key_here"

# Brevo SMTP Configuration
SMTP_SERVER="smtp-relay.brevo.com"
SMTP_PORT="587"
SMTP_LOGIN="your_brevo_login@smtp-brevo.com"
SMTP_PASSWORD="your_brevo_password"
SMTP_FROM_EMAIL="your_sender_email@domain.com"
```

### 3. Local Development Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r app/requirements.txt

# Run the MCP server
python app/gmail.py
```

### 4. Docker Deployment

```bash
# Build Docker image
docker build -t gmail-mcp-tool .

# Run container with environment variables
docker run -p 8000:8000 \
  -e SMTP_SERVER="eaxmple.com" \
  -e SMTP_PORT="587" \
  -e SMTP_LOGIN="your_login" \
  -e SMTP_PASSWORD="your_password" \
  -e SMTP_FROM_EMAIL="your_email@domain.com" \
  gmail-mcp-tool
```

## Usage

### MCP Server Endpoint

Once running, the MCP server will be available at:

```
http://localhost:8000/mcp
```

### Available Tools

#### `send_email_only`

Sends an email using the configured SMTP settings.

**Parameters:**

- `to_email` (required): Recipient email address
- `subject` (required): Email subject line
- `body` (required): Email content (supports plain text)
- `from_email` (optional): Sender email (defaults to SMTP_FROM_EMAIL)

**Example Usage:**

```python
# Via MCP client
result = mcp_client.call_tool("send_email_only", {
    "to_email": "recipient@example.com",
    "subject": "Hello from MCP",
    "body": "This is a test email sent via MCP!"
})
```

## Configuration

### Environment Variables

| Variable            | Description          | Required | Default                  |
| ------------------- | -------------------- | -------- | ------------------------ |
| `SMTP_SERVER`     | Brevo SMTP server    | Yes      | `smtp-relay.brevo.com` |
| `SMTP_PORT`       | SMTP port            | Yes      | `587`                  |
| `SMTP_LOGIN`      | Brevo SMTP login     | Yes      | -                        |
| `SMTP_PASSWORD`   | Brevo SMTP password  | Yes      | -                        |
| `SMTP_FROM_EMAIL` | Default sender email | No       | -                        |
| `ENV`             | Environment mode     | No       | `development`          |

### Brevo Setup

1. Sign up for a [Brevo account](https://www.brevo.com/)
2. Go to SMTP & API settings
3. Generate SMTP credentials
4. Use the provided login and password in your `.env` file

## Development

### Testing

Run the test script to verify email functionality:

```bash
python test.py
```

### Adding Features

The MCP server is built using FastMCP. To add new tools:

1. Define your function in `app/gmail.py`
2. Add the `@mcp.tool()` decorator
3. Restart the server

Example:

```python
@mcp.tool()
def new_email_feature(param1: str, param2: str) -> str:
    """
    Description of your new email feature
    """
    # Implementation here
    return "Success message"
```

## Troubleshooting

### Common Issues

1. **SMTP Authentication Failed**

   - Verify your Brevo credentials
   - Check if your Brevo account is active
   - Ensure SMTP is enabled in your Brevo account
2. **Port Connection Issues**

   - Make sure port 8000 is available
   - Check firewall settings
   - Try different ports if needed
3. **Environment Variables Not Loading**

   - Verify `.env` file exists and has correct format
   - Check file permissions
   - Ensure no extra spaces in variable assignments

### Logs

The server provides console output for debugging:

- ✅ Success messages for sent emails
- ❌ Error messages with details
- 🚀 Server startup information

## Security Notes

- Never commit `.env` files to version control
- Use environment variables in production
- Rotate SMTP credentials regularly
- Consider using secrets management in production

## License

This project is open source. Please check the license file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:

- Check the troubleshooting section
- Review Brevo documentation
- Create an issue in the repository

---

**Built with ❤️ using FastMCP and Brevo SMTP**
