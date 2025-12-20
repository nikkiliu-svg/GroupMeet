# GroupMeet Frontend

React + TypeScript frontend for GroupMeet study group matching platform.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file:
```
VITE_API_URL=http://localhost:5000
```

3. Run development server:
```bash
npm run dev
```

## Project Structure

- `src/components/` - React components
  - `auth/` - Authentication components
  - `forms/` - Form components
  - `dashboard/` - Dashboard components
  - `common/` - Common UI components
- `src/services/` - API client and types
- `src/hooks/` - Custom React hooks
- `src/utils/` - Utility functions

## Build

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

