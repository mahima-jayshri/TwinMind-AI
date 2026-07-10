# Deployment Guide

## Backend Deployment (Render)

### Prerequisites
- GitHub repository with the code
- Render account (free tier available)
- Google OAuth credentials
- Gemini API key

### Steps

1. **Prepare the Backend**
   - Ensure all environment variables are set in Render dashboard
   - Required variables:
     - `GOOGLE_CLIENT_ID`
     - `GOOGLE_CLIENT_SECRET`
     - `GEMINI_API_KEY`
     - `SECRET_KEY` (generate a random string)
     - `DATABASE_URL` (Render will provide PostgreSQL URL)
     - `FRONTEND_URL` (your deployed frontend URL)

2. **Deploy to Render**
   - Go to [render.com](https://render.com)
   - Click "New +"
   - Select "Web Service"
   - Connect your GitHub repository
   - Configure:
     - Name: twinmind-api
     - Runtime: Python 3
     - Build Command: `cd backend && pip install -r requirements.txt`
     - Start Command: `cd backend && python main.py`
   - Click "Deploy Web Service"

3. **Update Database**
   - Render will automatically run the startup event to initialize the database
   - Or manually trigger via Render shell

## Frontend Deployment (Vercel)

### Prerequisites
- Vercel account (free tier available)
- GitHub repository with the code

### Steps

1. **Prepare the Frontend**
   - Update `vite.config.js` to use production API URL
   - Add environment variable for API URL

2. **Deploy to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New Project"
   - Import your GitHub repository
   - Configure:
     - Framework Preset: Vite
     - Root Directory: frontend
     - Build Command: `npm run build`
     - Output Directory: dist
   - Add environment variable:
     - `VITE_API_URL`: your Render backend URL
   - Click "Deploy"

3. **Update CORS**
   - Update backend CORS settings to include your Vercel domain
   - In `backend/main.py`, add your Vercel URL to `allow_origins`

## Environment Variables

### Backend (.env)
```
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GEMINI_API_KEY=your_gemini_key
SECRET_KEY=random_secret_string
DATABASE_URL=postgresql://user:pass@host/db
FRONTEND_URL=https://your-frontend.vercel.app
```

### Frontend
```
VITE_API_URL=https://your-backend.onrender.com
```

## Production Considerations

### Security
- Use strong `SECRET_KEY`
- Enable HTTPS only
- Implement rate limiting
- Add input validation
- Use environment variables for secrets

### Database
- Use PostgreSQL in production (Render provides this)
- Set up regular backups
- Implement connection pooling
- Add database indexes for performance

### Scaling
- Use Redis for caching
- Implement CDN for static assets
- Add load balancing for high traffic
- Monitor performance with logging

### Monitoring
- Set up error tracking (Sentry)
- Add analytics (Google Analytics)
- Monitor API usage
- Set up alerts for failures

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure frontend URL is in backend CORS allow_origins
   - Check that API calls use correct base URL

2. **Database Connection**
   - Verify DATABASE_URL is correct
   - Check database is accessible
   - Ensure SSL is configured if required

3. **OAuth Failures**
   - Verify redirect URIs match exactly
   - Check Google Cloud Console settings
   - Ensure client ID and secret are correct

4. **Build Failures**
   - Check all dependencies are in requirements.txt/package.json
   - Verify build commands are correct
   - Check for version conflicts

## Domain Setup

### Custom Domain (Optional)

1. **Backend**
   - Purchase domain from registrar
   - Add custom domain in Render dashboard
   - Update DNS records as instructed

2. **Frontend**
   - Add custom domain in Vercel dashboard
   - Update DNS records as instructed
   - Enable SSL certificate (automatic)

## Cost Estimation

### Free Tier Usage
- Render: Free tier available (limited resources)
- Vercel: Free tier available (limited bandwidth)
- Google APIs: Free tier limits apply

### Paid Tier (if needed)
- Render: ~$7/month for basic web service
- Vercel: ~$20/month for pro plan
- Google APIs: Pay per usage

## Backup Strategy

### Database Backups
- Enable automatic backups in Render
- Export regular snapshots
- Store backups in secure location

### Code Backups
- GitHub serves as code backup
- Tag releases for version control
- Document deployment process

## Update Process

### Backend Updates
1. Push changes to GitHub
2. Render auto-deploys on push
3. Monitor deployment logs
4. Test new features

### Frontend Updates
1. Push changes to GitHub
2. Vercel auto-deploys on push
3. Preview deployment available
4. Promote to production when ready

## Rollback Plan

### If Deployment Fails
1. Render/Vercel automatically keeps previous version
2. Revert to previous commit if needed
3. Fix issues locally
4. Redeploy after testing

### Database Migrations
1. Create migration scripts
2. Test on staging first
3. Backup before migration
4. Run migration during low traffic
