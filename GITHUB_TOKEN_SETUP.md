# GitHub Token Setup for ClearCouncil Chat

## 🔧 Issue Found

Your GitHub token is missing the `models` permission required for GitHub Models API access.

**Error**: `The 'models' permission is required to access this endpoint`

## 🔑 How to Fix Your Token

### Step 1: Go to GitHub Token Settings
1. Visit: https://github.com/settings/tokens
2. Click on your existing token OR create a new one

### Step 2: Required Permissions
Make sure your token has these permissions:
- ✅ **repo** (Repository access)
- ✅ **user** (User information)
- ✅ **models** (Access to GitHub Models) ← **This is missing!**

### Step 3: Update Your Token
1. Click "Update token" or "Generate new token"
2. Check the `models` permission box
3. Save the token
4. Copy the new token value

### Step 4: Update Your .env File
Replace the token in your `.env` file:
```
GITHUB_TOKEN=your_new_token_with_models_permission
```

## 🎯 Alternative: Create New Token

If you prefer to create a fresh token:

1. **Go to**: https://github.com/settings/tokens
2. **Click**: "Generate new token" > "Generate new token (classic)"
3. **Name**: "ClearCouncil Chat"
4. **Expiration**: Choose your preference
5. **Select scopes**:
   - ✅ repo
   - ✅ user
   - ✅ models ← **Important!**
6. **Click**: "Generate token"
7. **Copy** the token immediately
8. **Add to .env**: `GITHUB_TOKEN=your_new_token`

## 🔍 Verify Token Works

After updating your token, test it:
```bash
python3 test_github_api.py
```

You should see:
```
✅ Success! Found X models
✅ GitHub Models API: WORKING
✅ Token: VALID
✅ Chat Application: READY
```

## 🚀 Once Fixed

After your token has the `models` permission:

1. **Update .env** with new token
2. **Test**: `python3 test_github_api.py`
3. **Install Flask**: `pip install flask flask-cors python-dotenv`
4. **Run app**: `python clearcouncil_chat.py`
5. **Open**: http://localhost:5002

## 💡 Why This Happened

GitHub Models is a relatively new feature, and the `models` permission is a special scope that wasn't included in your original token. This is a common issue when using existing tokens for new GitHub features.

## 🎉 What You'll Get

Once the token is fixed, you'll have:
- **Free AI chat** with GPT-4o-mini
- **Real-time responses** about your council data
- **Document search** through AI
- **Voting pattern analysis** via natural language
- **No ongoing costs** - completely free!

---

**Next**: Update your token with the `models` permission and test again!