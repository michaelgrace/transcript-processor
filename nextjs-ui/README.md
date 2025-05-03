# Next.js + Chakra UI Frontend Setup

This directory contains the new Next.js frontend for your app, using Chakra UI for the component library.

---

## 1. **Dependencies**

Install these in your `nextjs-ui` directory:

```bash
npm install @chakra-ui/react @emotion/react @emotion/styled framer-motion axios
```

---

## 2. **How to Run Next.js Locally**

```bash
cd nextjs-ui
npm install         # Installs dependencies (run once or after adding new deps)
npm run dev         # Starts Next.js in development mode (http://localhost:3000)
```

---

## 3. **How to Build for Production**

```bash
npm run build       # Builds the app for production
npm start           # Starts the production server
```

---

## 4. **Python requirements.txt**

- The `requirements.txt` file is **only for your Python backend** (FastAPI, Flask, Streamlit).
- **Node.js/React/Chakra UI dependencies are managed with `npm` in the `nextjs-ui` directory.**
- You do **not** add Chakra UI, axios, etc. to `requirements.txt`.

---

## 5. **Directory Structure (Recommended)**

```
nextjs-ui/
  ├── pages/         # Next.js routes
  ├── components/    # Reusable UI components
  ├── theme/         # Chakra UI theme config
  ├── utils/         # API helpers, etc.
  ├── public/        # Static assets (logo, etc.)
  ├── .env.local     # API URL and secrets
  └── README.md
```

---

## 6. **Environment Variables**

Create a `.env.local` file in `nextjs-ui/`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 7. **Chakra UI Setup**

In `pages/_app.js` (or `_app.tsx`):

```js
import { ChakraProvider } from "@chakra-ui/react";

function MyApp({ Component, pageProps }) {
  return (
    <ChakraProvider>
      <Component {...pageProps} />
    </ChakraProvider>
  );
}
export default MyApp;
```

---

## 8. **API Helper Example**

In `utils/api.js`:

```js
import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true, // if using cookies for auth
});

export default api;
```

---

## 9. **Next Steps**

- Scaffold your first page in `pages/` (e.g., `index.js`).
- Start migrating Streamlit UI features as Chakra UI React components.
- Use `api` helper for all backend calls.
- Keep this frontend directory separate from your backend code.

---

## 10. **Dockerfile-ui**

Already created at project root as `Dockerfile-ui` for containerized builds.

---

## 11. **You Can Now:**

- Build out your Next.js frontend in parallel with your existing app.
- Run `npm run dev` in `nextjs-ui/` for local development.
- Add new features, pages, and components without breaking your backend or other UIs.

---

**This setup is safe, modular, and ready for rapid development.**
