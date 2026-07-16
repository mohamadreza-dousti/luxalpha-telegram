### luxalpha
    Sale & License Management System

### How it Works (System Flow)

The system operates through a synchronized flow between the Telegram Bot, the FastAPI Backend, and the MetaTrader Expert Advisor (EA).

The Workflow:
1. Purchase: The customer interacts with the Telegram Bot to purchase a license or andicator.
2. License Generation: The bot communicates with the API to generate and store a unique license key in the database.
3. Activation: The customer enters this license key into the MetaTrader Expert Advisor (EA).
4. Validation: The EA sends a request to the API (`port 8000` or `8080`) to verify the license.
5. Access: If the license is valid, the API grants access, and the robot is activated on the trading platform.

---

### Project Structure

├── database/
│   └── db.py          
├── .env               
├── .gitignore        
├── README.md           
├── requirements.txt   
└── telegram.py     

---

### installation
    pip install -r requirements.txt

### envirment configuration
TOKEN=token
HOST=db-host
USERR=db-user
PASS=db-pass
DB=db name
PHOTO_GROUP_ID = photo-group-id
SUPPORT_GROUP_ID = support-group-id
VIP_ID = vip id
MANAGER_CHAT_ID = manager-chat-id
ME_CHAT_ID = me-chat-id
PHOTO_ID = andicator-photo-id
BOT_PHOTO_ID = bot-photo-id
PRO_BOT_PHOTO_ID = pro-bot-photo-id
VIDEO_ID = andicator-video-photo-id
ANDPDF = andicator-pdf-id
BOT_VIDEO_ID = bot-video-id
VOICE_ID = voice-id
EX_ID_PRO = ea-id-pro-bot
EX_ID = ea-id-bot

### running 
### -telegram-bot
    python3 telegram.py

### -api
    uvicorn main:app --host 0.0.0.0 --port 8000

### -pro-api
    uvicorn main:app --host 0.0.0.0 --port 8080
