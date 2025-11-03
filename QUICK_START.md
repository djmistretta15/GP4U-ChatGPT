# GP4U Quick Start Guide

## 🚀 Get GP4U Running in 15 Minutes

### Prerequisites Check
```bash
python --version  # Should be 3.11+
node --version    # Should be 18+
docker --version  # Optional but recommended
```

### Option 1: Docker (Recommended - Easiest)

```bash
# 1. Navigate to project
cd gp4u-complete

# 2. Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# 3. Start everything with one command
docker-compose up -d

# 4. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

That's it! The application is running with:
- PostgreSQL database
- Redis cache
- Backend API server
- Frontend development server

### Option 2: Manual Setup (More Control)

#### Backend Setup (5 minutes)

```bash
# 1. Navigate to backend
cd gp4u-complete/backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env and add your API keys:
# - STRIPE_SECRET_KEY
# - SENDGRID_API_KEY
# - DATABASE_URL (if not using default)

# 5. Set up database
# Make sure PostgreSQL is running, then:
alembic upgrade head

# 6. Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend is now running at http://localhost:8000

#### Frontend Setup (5 minutes)

```bash
# 1. Navigate to frontend (in a new terminal)
cd gp4u-complete/frontend

# 2. Install dependencies
npm install

# 3. Set up environment
cp .env.example .env.local
# Edit .env.local:
VITE_API_URL=http://localhost:8000
VITE_STRIPE_PUBLISHABLE_KEY=your_stripe_pk_test_key

# 4. Start development server
npm run dev
```

Frontend is now running at http://localhost:3000

#### Catalyst Network Setup (Optional - 5 minutes)

```bash
# 1. Navigate to catalyst
cd gp4u-complete/catalyst

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start services
python health_monitor.py &
python smart_router.py &
```

Catalyst Network is now running in the background.

### First-Time Setup Tasks

1. **Create Admin User**
```bash
# In backend directory
python scripts/create_admin.py
```

2. **Seed Sample Data** (Optional)
```bash
python scripts/seed_data.py
```

3. **Run Tests** (Optional but recommended)
```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test
```

## 📝 Configuration Checklist

### Required API Keys

1. **Stripe** (for payments)
   - Get keys from: https://dashboard.stripe.com/test/apikeys
   - Add to backend/.env:
     ```
     STRIPE_SECRET_KEY=sk_test_...
     STRIPE_PUBLISHABLE_KEY=pk_test_...
     ```
   - Add to frontend/.env.local:
     ```
     VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
     ```

2. **SendGrid** (for emails)
   - Get key from: https://app.sendgrid.com/settings/api_keys
   - Add to backend/.env:
     ```
     SENDGRID_API_KEY=SG....
     ```

3. **OAuth Providers** (optional)
   - Google: https://console.cloud.google.com/apis/credentials
   - GitHub: https://github.com/settings/developers
   - Add to backend/.env:
     ```
     GOOGLE_OAUTH_CLIENT_ID=...
     GOOGLE_OAUTH_CLIENT_SECRET=...
     GITHUB_OAUTH_CLIENT_ID=...
     GITHUB_OAUTH_CLIENT_SECRET=...
     ```

### Optional Configurations

4. **AWS S3** (for file storage)
   ```
   AWS_ACCESS_KEY_ID=...
   AWS_SECRET_ACCESS_KEY=...
   S3_BUCKET_NAME=gp4u-storage
   ```

5. **MapBox** (for location maps)
   - Get token from: https://account.mapbox.com/access-tokens/
   - Add to frontend/.env.local:
     ```
     VITE_MAPBOX_TOKEN=pk....
     ```

## 🎯 Verify Everything Works

### 1. Check Backend Health
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

### 2. Check Database Connection
```bash
curl http://localhost:8000/api/v1/health/db
# Should return: {"status": "connected"}
```

### 3. Open Frontend
Navigate to http://localhost:3000
- You should see the GP4U homepage
- Try signing up for an account
- Try browsing available GPUs

### 4. Check API Documentation
Navigate to http://localhost:8000/docs
- You should see interactive API documentation
- Try making a test API call

## 🐛 Troubleshooting

### Backend Won't Start

**Problem:** Port 8000 already in use
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9
# Or use a different port
uvicorn main:app --port 8001
```

**Problem:** Database connection error
```bash
# Check PostgreSQL is running
pg_isready
# Or use Docker
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:14
```

### Frontend Won't Start

**Problem:** Port 3000 already in use
```bash
# Kill the process or use different port
# Vite will ask if you want to use a different port
```

**Problem:** API calls failing
- Check VITE_API_URL in .env.local
- Make sure backend is running
- Check browser console for CORS errors

### Docker Issues

**Problem:** Containers won't start
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart

# Full reset
docker-compose down -v
docker-compose up -d
```

## 📚 Next Steps

1. **Read the Documentation**
   - [API Documentation](docs/API.md)
   - [User Guide](docs/USER_GUIDE.md)
   - [Developer Guide](docs/DEVELOPER_GUIDE.md)

2. **Explore the Code**
   - Backend API endpoints: `backend/api/`
   - Frontend components: `frontend/components/`
   - Catalyst Network: `catalyst/`

3. **Customize for Your Needs**
   - Modify branding and colors
   - Add custom GPU models
   - Configure payment settings
   - Set up production deployment

4. **Deploy to Production**
   - See [DEPLOYMENT.md](docs/DEPLOYMENT.md)
   - Set up SSL certificates
   - Configure production database
   - Set up monitoring and logging

## 🤝 Need Help?

- Check the documentation in `/docs`
- Review code templates in `FILE_TEMPLATES.md`
- See project structure in `PROJECT_INVENTORY.md`

## 🎉 You're All Set!

You now have a fully functional GPU rental marketplace running locally. Start exploring the codebase and customizing it for your needs!

**Happy coding!** 🚀
