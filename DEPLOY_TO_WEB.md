# Deploy TenderIntel to Web (Railway.app)
**Estimated Time:** 3 minutes  
**Cost:** $0 (completely free)

---

## 🚀 **One-Click Deploy Button**

Click this button to deploy TenderIntel to the internet:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/x-INFiN1TY-x/TenderIntel)

---

## 📋 **Alternative: Manual Deployment (3 Steps)**

### **Step 1: Sign Up / Login to Railway**

Go to: **https://railway.app**

- Click "Login with GitHub"
- Authorize Railway to access your GitHub account
- **That's it for setup!**

---

### **Step 2: Create New Project from GitHub**

1. On Railway dashboard, click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose: **`x-INFiN1TY-x/TenderIntel`**
4. Railway will automatically:
   - ✅ Detect Docker setup
   - ✅ Build your containers
   - ✅ Deploy API + Frontend
   - ✅ Provide public URLs

**Wait 2-3 minutes for build to complete.**

---

### **Step 3: Get Your Public URLs**

After build completes:

1. Click on your project
2. Click on the **"api"** service
3. Go to **Settings** → **Networking**
4. Click **"Generate Domain"**
5. You'll get: `https://tenderintel-api-production.up.railway.app`

Repeat for **"frontend"** service to get:
`https://tenderintel-production.up.railway.app`

---

## ✅ **What You'll Get:**

**Live API:**
- Public URL like: `https://your-project.up.railway.app`
- All 18 endpoints accessible
- Automatic HTTPS
- Health monitoring

**Live Frontend:**
- Professional web interface
- All 6,700+ lines of code running
- Search with 267 keywords
- Dashboard, heatmap, analytics
- Anyone can access via link

**Example:**
```bash
# Once deployed, anyone can use:
curl https://tenderintel-api-production.up.railway.app/search?q=cloud

# Or visit in browser:
https://tenderintel-production.up.railway.app
```

---

## 🎯 **After Deployment:**

**Share your live app:**
- Post on LinkedIn/Twitter
- Add to GitHub README
- Share with potential users

**Monitor usage:**
- Railway dashboard shows traffic
- View logs in real-time
- Check resource usage

**Auto-updates:**
- Push to GitHub → Railway auto-deploys
- No manual intervention needed

---

## 💡 **Environment Variables (Already Configured)**

Railway will automatically use your:
- ✅ Database: data/tenders.db (114 records)
- ✅ Configuration: config/synonyms.yaml (267 keywords)
- ✅ Ports: 8002 (API), 8080 (Frontend)

**No manual configuration needed!**

---

## 🔧 **Troubleshooting (If Needed):**

**If build fails:**
- Check Railway build logs
- Usually auto-fixes on retry

**If database empty:**
- Railway runs setup automatically
- Check logs for initialization messages

**If API not responding:**
- Check health endpoint: `/health`
- View Railway logs for errors

---

## 🎉 **Expected Result:**

**After 3 minutes:**
✅ TenderIntel live on the internet  
✅ Public URL anyone can access  
✅ Fully functional with all features  
✅ Automatic HTTPS  
✅ Free forever (within limits)

**Railway Free Tier Limits:**
- 500 hours/month (plenty for demo)
- $5 credit included
- No credit card required

---

## 📊 **Alternative Free Platforms:**

If Railway doesn't work:

**Fly.io:** https://fly.io (also free Docker deployment)  
**Render.com:** https://render.com (free for static sites)  
**Vercel:** https://vercel.com (good for frontend only)

---

**Ready to deploy?** Click the Railway button above or follow the 3-step manual process!
