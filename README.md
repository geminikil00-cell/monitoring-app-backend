# Monitoring App Backend

This is the FastAPI backend for the Parental Monitoring App.

## Deployment on Coolify

1. **Connect GitHub**: In Coolify, go to **Sources** and connect your GitHub account.
2. **Create New Project**: Create a new project in Coolify.
3. **Add Resource**: Select **Public GitHub Repository** or **Private** and point to this repo.
4. **Configuration**:
   - **Build Pack**: Select `Docker`.
   - **Environment Variables**: Add all variables from `.env.example`.
   - **Port**: Set to `8000`.
5. **Deploy**: Click Deploy.

## Environment Variables Needed
- `DATABASE_URL`: Supabase connection string.
- `SECRET_KEY`: Random secure string.
- `S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_ENDPOINT`: Cloudflare R2 credentials.
- `CORS_ORIGINS`: Your Cloudflare Pages URL.
