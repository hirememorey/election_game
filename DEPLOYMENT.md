# Deployment Guide for Election: The Game

This guide will help you deploy your game so it can be played on iPhone via a web browser.

## Option 1: Local Development (Testing)

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Server:**
   ```bash
   python server.py
   ```

3. **Access on iPhone:**
   - Make sure your iPhone and computer are on the same WiFi network
   - Find your computer's local IP address (e.g., 192.168.1.100)
   - On your iPhone, open Safari and go to: `http://192.168.1.100:5000`

## Option 2: Deploy to Render (Recommended for Production)

### Backend Deployment (Render)

1. **Create a Render Account:**
   - Go to [render.com](https://render.com) and sign up

2. **Create a New Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Set the following:
     - **Name:** election-game
     - **Environment:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `python server.py`
     - **Plan:** Free

3. **Environment Variables:**
   - Add `PORT=10000` (Render uses port 10000)

4. **Update server.py for Production:**
   ```python
   if __name__ == '__main__':
       port = int(os.environ.get('PORT', 5000))
       app.run(host='0.0.0.0', port=port)
   ```

### Frontend Deployment (Netlify)

1. **Create a Netlify Account:**
   - Go to [netlify.com](https://netlify.com) and sign up

2. **Deploy Static Files:**
   - Drag and drop the `static` folder to Netlify
   - Or connect your GitHub repository and set build settings

3. **Update API URL:**
   - In `static/script.js`, change:
   ```javascript
   const API_BASE_URL = 'https://your-render-app.onrender.com/api';
   ```

## Option 3: Deploy to Heroku

1. **Install Heroku CLI:**
   ```bash
   # macOS
   brew install heroku/brew/heroku
   ```

2. **Create Heroku App:**
   ```bash
   heroku create your-election-game
   ```

3. **Add Procfile:**
   Create a file named `Procfile` (no extension):
   ```
   web: python server.py
   ```

4. **Deploy:**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

5. **Update API URL:**
   - In `static/script.js`, change to your Heroku URL

## Option 4: Deploy to Railway

1. **Create Railway Account:**
   - Go to [railway.app](https://railway.app) and sign up

2. **Deploy:**
   - Connect your GitHub repository
   - Railway will automatically detect Python and deploy

3. **Update API URL:**
   - Use the provided Railway URL

## Testing on iPhone

1. **Open Safari** on your iPhone
2. **Navigate** to your deployed URL
3. **Add to Home Screen** (optional):
   - Tap the share button
   - Select "Add to Home Screen"
   - This creates an app-like experience

## Troubleshooting

### CORS Issues
If you see CORS errors, make sure:
- The frontend and backend URLs match
- CORS is properly configured in `server.py`

### API Connection Issues
- Check that the `API_BASE_URL` in `script.js` points to your deployed backend
- Verify the backend is running and accessible

### Mobile Display Issues
- The CSS is already mobile-optimized
- Test in Safari's responsive design mode
- Check that viewport meta tag is present

## Security Notes

For production deployment:
1. **Use HTTPS** (most platforms provide this automatically)
2. **Add rate limiting** to prevent abuse
3. **Consider adding authentication** if needed
4. **Use environment variables** for sensitive data

## Performance Tips

1. **Enable gzip compression** on your hosting platform
2. **Use a CDN** for static assets
3. **Optimize images** if you add any
4. **Consider caching** for game state

## Next Steps

Once deployed, you can:
1. Share the URL with friends to play together
2. Add more features like game history
3. Implement real-time multiplayer using WebSockets
4. Add sound effects and animations 