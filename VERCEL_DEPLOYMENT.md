# Deploying DreamOS to Vercel

This guide will help you deploy DreamOS to Vercel.

## Prerequisites

- A Vercel account
- Git repository for your DreamOS project
- Vercel CLI (optional)

## Deployment Steps

### 1. Using the Vercel Dashboard

1. Push your DreamOS code to a Git repository (GitHub, GitLab, or Bitbucket)
2. Log in to your Vercel account
3. Click "New Project"
4. Import your Git repository
5. Configure your project:
   - Framework Preset: Other
   - Build Command: Leave empty
   - Output Directory: Leave empty
   - Install Command: `pip install -r requirements.txt`
   - Development Command: Leave empty
6. Add required environment variables under "Environment Variables":
   - `SECRET_KEY`: A secure random string for Flask session encryption
   - `FLASK_ENV`: Set to "production" for deployment
   - Any API keys required by your application (check your current .env file)
7. Click "Deploy"

### 2. Using Vercel CLI

If you prefer using the command line:

1. Install Vercel CLI:
   ```
   npm i -g vercel
   ```

2. Navigate to your project directory:
   ```
   cd path/to/DreamOS-Operating-System-of-Agents
   ```

3. Login to Vercel:
   ```
   vercel login
   ```

4. Deploy your project:
   ```
   vercel
   ```

5. Follow the interactive prompts and select appropriate options.

## Configuration Files

The following configuration files have been added to your project for Vercel deployment:

- `vercel.json`: Main configuration file for Vercel
- `vercel_app.py`: Entry point for the Vercel serverless function
- `wsgi.py`: WSGI configuration for compatibility
- `runtime.txt`: Specifies the Python version

## Important Notes

1. **Socket.IO Support**: Vercel's serverless functions have limitations with WebSockets and Socket.IO. The application has been configured to use long polling as the primary transport method.

2. **File System Limitations**: Vercel's serverless functions have read-only file systems. Any file writing operations in your application will fail. Consider these alternatives:
   - For memory persistence: Use a MongoDB Atlas free tier or Redis Cloud for storing DreamOS memory
   - For file storage: Use AWS S3, Google Cloud Storage, or other cloud storage services
   - For temporary storage: Use `/tmp` directory, but note it has a size limit and is not persistent across function invocations

3. **Cold Starts**: Serverless functions experience cold starts. The first request after a period of inactivity may take longer to respond.

4. **Execution Time Limits**: Vercel imposes a maximum execution time for serverless functions (currently 10 seconds for the Hobby plan). Long-running operations need to be adapted:
   - Break down operations into smaller chunks
   - Use background processing with a queue service like AWS SQS or RabbitMQ
   - Consider upgrading to a paid plan for longer execution times

5. **Memory Limitations**: Memory usage is limited to 1GB per serverless function invocation.

6. **Environment Variables**: Make sure to set all required environment variables in the Vercel dashboard:
   - API keys
   - Database connection strings
   - Storage credentials
   - `SECRET_KEY` for Flask sessions

## Troubleshooting

If you encounter issues during deployment:

1. Check the Vercel deployment logs for error messages
2. Ensure all required environment variables are properly set
3. Verify that your application doesn't rely on file system writes in the application directory
4. Consider using Vercel's CLI with the `--debug` flag for more detailed logs 