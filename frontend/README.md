# 🌍 Carbon Credit Frontend - Next.js

Beautiful, modern web application for the Carbon Credit Blockchain Verification System.

## 🎨 Features

### 3 User Portals

1. **Field Worker Portal** (`/worker`)
   - Submit tree planting verifications
   - Capture photos and GPS data
   - Biometric gesture verification
   - Real-time NFT minting

2. **NGO Manager Dashboard** (`/ngo`)
   - Monitor all worker verifications
   - Review pending submissions
   - Generate reports for donors
   - Track system health

3. **Corporate Marketplace** (`/corporate`)
   - Browse verified carbon credits
   - Purchase NFT-backed credits
   - Generate ESG reports
   - Track carbon offset goals

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Backend API running on port 8000 (see `../` directory)

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Open browser
# http://localhost:3000
```

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## 📁 Project Structure

```
frontend/
├── app/
│   ├── page.tsx              # Landing page
│   ├── worker/page.tsx       # Worker verification portal
│   ├── ngo/page.tsx          # NGO management dashboard
│   ├── corporate/page.tsx    # Corporate marketplace
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
├── utils/
│   └── api.ts                # API client for backend
├── package.json
├── next.config.js
├── tailwind.config.ts
└── tsconfig.json
```

## 🔌 API Integration

The frontend connects to your Python FastAPI backend running on `localhost:8000`.

### Environment Variables

The API URL is configured in `next.config.js`:

```javascript
env: {
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
}
```

To change the API URL:

```bash
# Create .env.local (optional)
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

### Available API Endpoints

All API calls are in `utils/api.ts`:

```typescript
import { api } from '@/utils/api';

// Health check
await api.healthCheck();

// Upload image
await api.uploadImage(file, workerId);

// Submit verification
await api.submitVerification({
  trees_planted: 25,
  location: "Mumbai, India",
  gps_coords: "19.076, 72.877",
  worker_id: "WORKER001",
  image_url: "...",
});

// Get worker history
await api.getWorkerHistory("WORKER001");

// Get system stats
await api.getStats();
```

## 🎨 Styling

- **Framework**: Tailwind CSS
- **Icons**: Lucide React
- **Design**: Modern gradient UI with shadcn/ui principles

### Color Scheme

```css
Primary (Green): #059669 (for environmental theme)
Secondary (Blue): #3B82F6 (for trust/tech)
Accent (Purple): #9333EA (for premium features)
```

## 📱 Pages Overview

### 1. Landing Page (`/`)

- Hero section with stats
- Feature highlights
- Three portal links
- Call-to-action buttons

### 2. Worker Portal (`/worker`)

**Multi-step verification flow:**

1. **Step 1: Enter Details**
   - Worker ID
   - Number of trees
   - Location (with GPS auto-detect)

2. **Step 2: Capture Photo**
   - Webcam capture OR file upload
   - Preview before submission

3. **Step 3: Gesture Verification**
   - Hand gesture biometric (simulated)
   - Progress indicator (5 gestures required)

4. **Step 4: Processing**
   - Real-time validation status
   - Submits to backend API

5. **Step 5: Result**
   - Success: Shows NFT ID, carbon offset, explorer link
   - Failure: Shows error message with retry option

### 3. NGO Dashboard (`/ngo`)

**Dashboard sections:**

- **Stats Overview**: Total verifications, workers, CO₂ offset, value
- **Pending Reviews**: Claims that need manual approval
- **Recent Verifications**: Latest submissions with status
- **Top Performers**: Best workers by tree count
- **Quick Actions**: Generate reports, manage workers, analytics
- **System Health**: API, blockchain, AI status

### 4. Corporate Marketplace (`/corporate`)

**Marketplace features:**

- **Portfolio Summary**: Carbon offset goals, total credits, investment
- **Search & Filter**: Find projects by location, price, verification
- **Available Batches**: Grid of carbon credit NFT batches
  - Each batch shows: trees, location, verification methods, price
  - Confidence score indicator
  - Purchase button
- **ESG Report**: Download PDF for compliance

## 🔧 Customization

### Add New API Endpoint

Edit `utils/api.ts`:

```typescript
// Add to CarbonCreditAPI class
async newEndpoint(param: string) {
  const response = await fetch(`${this.baseURL}/new-endpoint/${param}`);
  return response.json();
}
```

### Add New Page

```bash
# Create new page
mkdir app/newpage
touch app/newpage/page.tsx
```

```typescript
// app/newpage/page.tsx
export default function NewPage() {
  return <div>New Page</div>;
}
```

Access at: `http://localhost:3000/newpage`

### Modify Styles

Global styles are in `app/globals.css`. Component-specific styles use Tailwind utility classes.

## 📦 Dependencies

```json
{
  "next": "14.1.0",              // React framework
  "react": "^18.2.0",            // UI library
  "typescript": "^5.3.3",        // Type safety
  "tailwindcss": "^3.4.1",       // Styling
  "lucide-react": "^0.323.0",    // Icons
  "react-webcam": "^7.2.0",      // Camera access
  "axios": "^1.6.5",             // HTTP client
  "recharts": "^2.10.3"          // Charts (for analytics)
}
```

## 🚀 Deployment

### Option 1: Vercel (Recommended for Next.js)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Your app is live at: https://your-app.vercel.app
```

### Option 2: Docker

```dockerfile
# Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

```bash
# Build and run
docker build -t carbon-credit-frontend .
docker run -p 3000:3000 carbon-credit-frontend
```

### Option 3: Traditional Server

```bash
# Build
npm run build

# Copy .next/ and node_modules/ to server
# Start with PM2
pm2 start npm --name "carbon-frontend" -- start
```

## 🔒 Security Notes

- API calls use HTTPS in production
- No sensitive data stored in localStorage
- API keys never exposed to frontend
- CORS configured in backend API

## 🐛 Troubleshooting

### API Connection Issues

```bash
# Check if backend is running
curl http://localhost:8000/

# Check CORS settings in backend
# Add your frontend URL to allow_origins in api.py
```

### Build Errors

```bash
# Clear cache
rm -rf .next node_modules
npm install
npm run dev
```

### Webcam Not Working

- Browser must be HTTPS or localhost
- User must grant camera permission
- Check browser console for errors

## 📝 To-Do / Future Enhancements

- [ ] Real MediaPipe gesture detection
- [ ] WebSocket for real-time updates
- [ ] User authentication (JWT)
- [ ] Database persistence (show real data)
- [ ] Mobile-responsive improvements
- [ ] Dark mode toggle
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Notification system
- [ ] Export data to CSV/PDF

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

MIT License - feel free to use for your projects

## 🙏 Credits

Built with ❤️ for a sustainable future

- **Framework**: Next.js 14
- **Styling**: Tailwind CSS
- **Icons**: Lucide
- **Blockchain**: Algorand
- **AI**: OpenAI GPT-4

---

**Ready to change the world? Start the dev server and visit http://localhost:3000** 🌱
