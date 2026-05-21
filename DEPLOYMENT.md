# Deployment Guide: PharmaCare Ecommerce

This guide explains how to deploy the PharmaCare platform to a real-world market environment.

## 1. Prerequisites
- Domain Name
- SSL Certificate (managed by your hosting provider)
- Managed Database (AWS RDS, Render Postgres, etc.)
- Razorpay Account (Live Keys)

## 2. Environment Configuration
Ensure your `.env` file contains production values:
```env
DEBUG=False
SECRET_KEY=your-long-secure-random-key
ALLOWED_HOSTS=yourdomain.com
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
DB_HOST=...
DB_PORT=5432
RAZOR_KEY_ID=rzp_live_...
RAZOR_KEY_SECRET=...
```

## 3. Deployment Options

### Option A: Render (Easiest)
1. Connect your GitHub repo to Render.
2. Select **Web Service**.
3. Use the following:
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start Command: `gunicorn pharmacy_project.wsgi:application`
4. Add all environment variables in the Render Dashboard.

### Option B: AWS / DigitalOcean (Using Docker)
1. Push your Docker image to a registry (ECR/DockerHub).
2. Provision an EC2/Droplet.
3. Use the provided `docker-compose.yml` to spin up the web and database services.

## 4. Post-Deployment Checklist
- [ ] Run `python import_medicines.py` to populate initial data.
- [ ] Create a Django Superuser: `python manage.py createsuperuser`.
- [ ] Verify SSL (HTTPS) is working.
- [ ] Test a small real transaction with Razorpay Live mode.
- [ ] Configure a CDN (Cloudflare) for better performance.
