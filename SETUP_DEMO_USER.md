# Quick Setup for Demo Login

## Create Test User

Run this command in your terminal:

```bash
cd "/Users/pratikkumar/Desktop/Antenna Designer/backend"
source venv/bin/activate
python create_test_user.py
```

This creates a test user:
- **Email:** `test@example.com`
- **Password:** `test123`

## Use Demo Login

1. Go to the login page
2. Click the **"🚀 Demo Login (Bypass Registration)"** button
3. You'll be automatically logged in!

## Troubleshooting

**If demo login fails:**
1. Make sure the backend is running (check terminal for `Uvicorn running on http://0.0.0.0:8000`)
2. Make sure you ran `create_test_user.py` successfully
3. Check browser console (F12) for errors
4. Check backend terminal for error messages

## Manual Login

You can also manually enter:
- Email: `test@example.com`
- Password: `test123`





