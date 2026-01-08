# Dechivo Frontend

A React-based frontend for the Dechivo SFIA-powered job description enhancement platform.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📁 Project Structure

```
frontend/src/
├── App.jsx              # Root component with routing
├── AuthContext.jsx      # Authentication context provider
├── analytics.js         # Mixpanel analytics utilities
├── main.jsx             # Application entry point
│
├── pages/               # Page components
│   ├── LandingPage.jsx      # Home page with hero section
│   ├── EnhancementPage.jsx  # JD editor with org context
│   ├── LoginPage.jsx        # User login
│   ├── RegisterPage.jsx     # User registration
│   └── ProtectedRoute.jsx   # Auth route wrapper
│
├── styles/              # CSS stylesheets
│   ├── index.css            # Global styles
│   ├── App.css              # App-level styles
│   ├── LandingPage.css      # Landing page styles
│   ├── EnhancementPage.css  # Enhancement page styles
│   ├── LoginPage.css        # Login page styles
│   └── RegisterPage.css     # Register page styles
│
└── assets/              # Static assets
```

## ⚙️ Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.x | UI Framework |
| Vite | 7.x | Build Tool & Dev Server |
| React Router | 6.x | Client-side Routing |
| Mammoth.js | - | DOCX file parsing |
| PDF.js | - | PDF file parsing |
| Mixpanel | - | Analytics tracking |

## 🎨 Design System

- **Brand**: Dechivo (lowercase 'c')
- **Colors**: Blue (#3B82F6) to Purple (#8B5CF6) gradients
- **Font**: Inter (Google Fonts)
- **Icons**: Inline SVG components
- **Responsive**: Mobile-first design

---

## 📋 Implementation Details

### Page 1: Landing Page (`/`)

**File**: `src/pages/LandingPage.jsx`

**Features**:
- Premium hero section with SFIA messaging
- "Enhance Your ICT Job Descriptions" headline
- Two action buttons:
  - **Load JD File**: Upload .txt, .pdf, .docx files
  - **Enhance JD**: Navigate to enhancement page
- Clean navigation (Home, About, Contact)
- Professional footer with Dechivo branding

### Page 2: Enhancement Page (`/enhance`)

**File**: `src/pages/EnhancementPage.jsx`

**Features**:
- **Organizational Context Form**: Collapsible panel with fields for:
  - Company information (name, industry, culture, values)
  - Role details (type, grade, reporting structure)
  - Work environment (location, remote/hybrid/onsite)
- **JD Editor**: Large textarea with character count
- **Action Buttons**:
  1. **Enhance** - Submit to backend for SFIA enhancement
  2. **Edit JD** - Edit mode (placeholder)
  3. **Publish** - Publish functionality (placeholder)
  4. **Download** - Save as .txt file
- Loading spinner overlay during processing
- Status notifications (success/error/info)
- Backend message display

### Page 3: Login Page (`/login`)

**File**: `src/pages/LoginPage.jsx`

**Features**:
- Email/username login
- JWT token authentication
- Error handling and validation
- Link to registration

### Page 4: Register Page (`/register`)

**File**: `src/pages/RegisterPage.jsx`

**Features**:
- Email, username, password registration
- Full name and organization fields
- Password confirmation
- Validation feedback

## 🔐 Authentication

- **Provider**: `AuthContext.jsx`
- **Method**: JWT with access/refresh tokens
- **Storage**: localStorage
- **Auto-refresh**: Tokens refresh before expiry

## 📊 Analytics (Mixpanel)

**File**: `src/analytics.js`

Events tracked:
- User signup/login/logout
- File uploads
- Enhancement started/completed/failed
- JD downloads

Mixpanel is configured for EU data residency (`api-eu.mixpanel.com`).

## 🔄 Navigation Flow

```
Landing Page (/)
    ├── Login (/login) → Enhancement Page
    ├── Register (/register) → Enhancement Page
    └── Enhance JD (with file) → Enhancement Page (/enhance)

Enhancement Page (/enhance) [Protected]
    ├── Fill org context
    ├── Click Enhance → Backend API
    ├── Download enhanced JD
    └── Logout → Landing Page
```

## 🌐 API Integration

All API calls go through `authenticatedFetch` in AuthContext:
- Automatically adds JWT Bearer token
- Handles token refresh on 401
- Redirects to login on auth failure

**Endpoints used**:
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/refresh` - Token refresh
- `POST /api/auth/logout` - User logout
- `POST /api/enhance-jd` - JD enhancement

## 🛠️ Development

### Environment Variables

Create `.env.local` for development:
```bash
VITE_API_URL=http://localhost:5000
VITE_MIXPANEL_TOKEN=your-token-here
```

### ESLint Configuration

ESLint is configured with React plugin. Extend in `eslint.config.js`.

### Adding New Pages

1. Create component in `src/pages/NewPage.jsx`
2. Create styles in `src/styles/NewPage.css`
3. Add route in `src/App.jsx`
4. Wrap with `ProtectedRoute` if auth required

## 📦 Build & Deploy

```bash
# Build for production
npm run build

# Output in /dist folder
# Deploy dist/ to any static hosting
```

For production deployment, the build is served by Nginx on the VPS with the backend API proxied at `/api/*`.
