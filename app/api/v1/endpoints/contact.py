from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.api import deps
from app.models.profiles import Profile

router = APIRouter()

class ContactRequest(BaseModel):
    email: Optional[EmailStr] = None
    message: str

# Email Configuration
SMTP_SERVER = "mail.urbanvibe.cl"
SMTP_PORT = 465
SMTP_USERNAME = "contacto@urbanvibe.cl"
SMTP_PASSWORD = "Abb1582esm.ComUV"

def send_email_task(subject: str, body: str, to_email: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            
    except Exception as e:
        print(f"Error sending email: {e}")
        # In a real app, we might want to log this to a file or monitoring service

@router.post("/")
async def send_contact_email(
    request: ContactRequest,
    background_tasks: BackgroundTasks,
    current_user: Optional[Profile] = Depends(deps.get_current_user_optional)
):
    """
    Send a contact email.
    If user is logged in, use their email.
    If not, require email in request.
    """
    
    sender_email = None
    sender_name = "Anonymous"
    
    if request.email:
        sender_email = request.email
        if current_user:
            sender_name = current_user.display_name or current_user.username or "User"
        else:
            sender_name = "Guest"
    elif current_user:
        # Fallback if for some reason request.email is missing but user is logged in
        # Note: Profile model might not have email, so we rely on request.email mostly
        sender_email = getattr(current_user, 'email', None)
        sender_name = current_user.display_name or current_user.username or "User"
        
    if not sender_email:
        raise HTTPException(status_code=400, detail="Email is required")
        
    subject = f"Nuevo mensaje de contacto de {sender_name}"
    body = f"""
    Nuevo mensaje recibido desde la App UrbanVibe:
    
    De: {sender_name} ({sender_email})
    
    Mensaje:
    {request.message}
    """
    
    # Send email in background to avoid blocking the request
    background_tasks.add_task(send_email_task, subject, body, SMTP_USERNAME)
    
    return {"message": "Mensaje enviado correctamente"}
