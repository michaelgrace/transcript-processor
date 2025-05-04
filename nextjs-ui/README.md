# Next.js + Chakra UI Frontend Setup

This directory contains the new Next.js frontend for your app, using Chakra UI for the component library.

---

## Quickstart

npm install
npm run dev

---

## Troubleshooting: "npm: The term 'npm' is not recognized..."

**This error means Node.js (and npm) is not installed or not in your system PATH.**

### **How to Fix**

1. **Install Node.js:**
   - Download and install Node.js from [https://nodejs.org/](https://nodejs.org/).
   - This will also install `npm`.

2. **Restart your terminal** (PowerShell, Command Prompt, etc.).

3. **Verify installation:**
   ```sh
   node -v
   npm -v
   ```
   Both commands should print version numbers.

4. **Now you can run:**
   ```sh
   npm install
   npm run dev
   ```

---

**Note:**  
- If you are using Docker, you do **not** need to run `npm install` or `npm run dev` on your host.  
- For local development (without Docker), Node.js and npm must be installed on your machine.

---

## Troubleshooting: Dark Theme Works, But Page Changes Do Not Show

---

## What This Means

- **Dark theme appears in private/incognito mode:**  
  Chakra UI’s color mode is being set and stored correctly.
- **Your code changes (e.g., edits to `pages/index.js`) do NOT show up, even after saving and refreshing:**  
  This means **hot reload is not working** or your container is not seeing file changes.

---

## Most Likely Causes

1. **Volume Mapping Issue:**  
   - Your Docker Compose volume for `nextjs-ui` may not be pointing to the directory you are editing.
   - Double-check that you are editing files in `/home/micha/transcript-processor/nextjs-ui` (WSL2), and that your volume mapping is:
     ```yaml
     volumes:
       - /home/micha/transcript-processor/nextjs-ui:/app
     ```

2. **VS Code Editing Wrong Location:**  
   - If you are editing files in Windows (`D:\...`) but your container is running from WSL2 (`/home/micha/...`), changes will not be reflected.
   - Open your project in VS Code using the "Remote - WSL" extension and edit files in `/home/micha/transcript-processor/nextjs-ui`.

3. **Browser Cache:**  
   - If you see dark mode but not code changes, it’s almost always a file sync issue, not a browser cache issue.

---

## What To Do

1. **Confirm you are editing the correct files:**
   - In your WSL2 terminal, run:
     ```sh
     ls -l /home/micha/transcript-processor/nextjs-ui/pages/index.js
     ```
   - Edit this file and add a unique string (e.g., "TEST123").
   - Save and check if it appears in the browser after refresh.

2. **Check Docker Compose volume mapping:**
   - Your `docker-compose.yml` for `nextjs-ui` should have:
     ```yaml
     volumes:
       - /home/micha/transcript-processor/nextjs-ui:/app
     ```

3. **Restart the Next.js container:**
   ```sh
   docker-compose up nextjs-ui
   ```

4. **If changes still do not show:**
   - You are likely editing a different copy of the project than what the container is using.
   - Use `pwd` in your VS Code terminal to confirm your working directory.

---

## Summary Table

| Symptom                  | Cause                              | Solution                        |
|--------------------------|------------------------------------|----------------------------------|
| Dark mode works          | Chakra UI config is correct         | No action needed                 |
| Page changes not visible | Editing wrong directory or volume   | Edit files in `/home/micha/...`  |
|                          | Volume mapping mismatch            | Fix `docker-compose.yml`         |

---

**Once you are editing the correct files in the correct location, hot reload and code changes will work as expected.**

---

## Structure

- `pages/` - Next.js routes
- `components/` - Reusable UI components
- `theme/` - Chakra UI theme config
- `utils/` - API helpers, etc.
- `public/` - Static assets (logo, etc.)
- `.env.local` - API URL and secrets

## Chakra UI Setup

See `pages/_app.js` for ChakraProvider usage.

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

## 11. **Development Workflow: See Changes Instantly**

- **For local development, you do NOT need to rebuild the Docker container for every change.**
- Instead, run the Next.js dev server locally (outside Docker):

```bash
cd nextjs-ui
npm install        # Only needed once
npm run dev
```

- Visit [http://localhost:3000](http://localhost:3000) in your browser.
- **Any changes you make to `.js`, `.jsx`, `.ts`, `.tsx`, or markup files will be hot-reloaded automatically.**
- You will see updates in the browser as soon as you save your files.

---

# Understanding Next.js Hot Reload and Fast Refresh Warnings in Docker

---

## What Your Log Means

- `GET /_next/static/webpack/....hot-update.json 404`  
  This is **normal** during hot reload: Next.js looks for a hot update file, and if it doesn't exist (e.g., after a full reload), it falls back to a full page reload.

- `⚠ Fast Refresh had to perform a full reload.`  
  This means Next.js couldn't do a "hot update" and instead reloaded the whole page.  
  **This is not an error**—your changes are still picked up, but the browser reloads instead of updating just the changed component.

---

## Why Does This Happen?

- **In Docker, especially with volume mounts,** file watching can be less reliable than on native Linux/macOS.
- Sometimes, Next.js can't detect a "safe" hot update and falls back to a full reload.
- This is common and expected in Docker/WSL2 setups, especially after large changes or dependency updates.

---

## What Should You Do?

- **If your changes appear after saving and the browser reloads, hot reload is working (even if it's a full reload).**
- If you see your edits reflected after a few seconds, your setup is correct.
- If you want to reduce full reloads:
  - Make smaller, more incremental changes.
  - Avoid editing files outside the `pages/` or `components/` directories unless necessary.
  - Make sure your project is in your WSL2 home directory (which you have done).

---

## When to Worry

- If changes **never** appear after saving, or you always have to restart the container, then hot reload is broken.
- If you only see a full reload (not a hot update), but changes appear, this is normal in Docker.

---

## Summary Table

| Log Message/Warn                | What It Means                | Action Needed         |
|---------------------------------|------------------------------|----------------------|
| 404 hot-update.json             | Normal, triggers full reload | None                 |
| Fast Refresh had to perform...  | Full reload instead of HMR   | None (if changes show)|
| Changes appear after save       | Hot reload is working        | None                 |
| Changes never appear            | Hot reload broken            | Troubleshoot further  |

---

**Bottom line:**  
- Your setup is working as expected if changes show up after saving, even if you see these warnings.
- These logs are informational and not errors.

---

# Docker, Next.js, and Hot Reload: Manual Steps vs. Automation

---

## **Why Are Manual Steps Needed?**

- **Volume mapping (`/home/micha/transcript-processor/nextjs-ui:/app`)** overwrites the container’s `/app` directory with your local files.
- This means any `node_modules` installed during the Docker build are hidden by the volume mapping.
- You must run `npm install` inside the container (with the volume mounted) to ensure dependencies are present for hot reload.

---

## **Can This Be Automated?**

**Yes, you can automate this with an entrypoint script in your Dockerfile:**

1. **Create an entrypoint script** (e.g., `entrypoint.sh`) in your `nextjs-ui` directory:
   ```bash
   #!/bin/sh
   if [ ! -d "node_modules" ]; then
     npm install
   fi
   exec "$@"
   ```

2. **Update your Dockerfile-ui** to copy and use this script:
   ```dockerfile
   # ...existing code...
   COPY nextjs-ui/ ./ 
   COPY nextjs-ui/entrypoint.sh /entrypoint.sh
   RUN chmod +x /entrypoint.sh
   # ...existing code...
   ENTRYPOINT ["/entrypoint.sh"]
   CMD ["npx", "next", "dev"]
   ```

3. **Now, when you run `docker-compose up nextjs-ui`,** the container will automatically run `npm install` if `node_modules` is missing, and then start the dev server.

---

## **Summary Table**

| Approach                | Manual `npm install` | Automated | Hot Reload | Recommended for Dev |
|-------------------------|----------------------|-----------|------------|--------------------|
| Current (manual)        | Yes                  | No        | Yes        | OK                 |
| With entrypoint script  | No                   | Yes       | Yes        | **Best**           |

---

**Bottom line:**  
- Docker Compose and Dockerfile can automate dependency installation for hot reload in dev.
- Use an entrypoint script to check/install `node_modules` automatically.
- This way, you do NOT have to run `npm install` manually every time.

---

# Running Docker Compose in WSL Terminal vs Windows Terminal

---

## **Is it the same?**

**No, running `docker-compose` from your WSL terminal is NOT exactly the same as running it from your Windows terminal.**

---

## **Key Differences**

- **WSL Terminal:**
  - Uses the Linux file system and environment.
  - File paths like `/home/micha/...` are native and fast.
  - File watching (hot reload) and Docker volume mounts are more reliable for Node.js/Next.js projects.
  - Recommended for best performance and developer experience with Docker, Next.js, and Python.

- **Windows Terminal (CMD/PowerShell):**
  - Uses Windows file system and environment.
  - File paths like `D:\...` or `C:\...` are native.
  - Docker Desktop bridges between Windows and WSL2, but file watching and volume mounts can be slower or unreliable for hot reload.
  - May cause issues with Next.js hot reload and file syncing.

---

## **Summary Table**

| Terminal Used      | File Paths Used         | Hot Reload Reliability | Recommended For...         |
|--------------------|------------------------|-----------------------|----------------------------|
| WSL2 Terminal      | `/home/micha/...`      | High                  | Next.js, Docker, Python    |
| Windows Terminal   | `D:\...` or `C:\...`   | Low/Unreliable        | Windows-native workflows   |

---

## **Best Practice**

- **Always run Docker Compose and development commands from your WSL2 terminal** when your project is in your WSL2 home directory.
- This ensures the best compatibility, performance, and hot reload for your Next.js and Python apps.

---

**In summary:**  
Running in WSL2 is the recommended and most reliable way for your current setup.

---

# Final Steps: Full No-Cache Build and Checklist

---

## 1. **Do a Full No-Cache Build**

After all the changes (entrypoint script, Dockerfile, volume mapping, project location), you should do a clean build to ensure everything is up to date:

```sh
docker-compose build --no-cache
docker-compose up
```

---

## 2. **Checklist Before/After Build**

- [x] **Project is in `/home/micha/transcript-processor` (WSL2 home)**
- [x] **Docker Compose volume for `nextjs-ui` is `/home/micha/transcript-processor/nextjs-ui:/app`**
- [x] **`entrypoint.sh` is present in `nextjs-ui/` and executable**
- [x] **Dockerfile-ui uses the entrypoint script and `npx next dev`**
- [x] **All dependencies are listed in `package.json`**
- [x] **No manual `npm install` needed after this build**
- [x] **You can edit files in VS Code (WSL) and see hot reload in the browser**

---

## 3. **What Else?**

- **No further manual steps should be needed for hot reload or dependency install.**
- If you add new dependencies, just update `package.json` and rebuild.
- For production, adjust the Dockerfile and Compose to use `npm run build` and `npx next start` instead of `dev`.

---

## 4. **If You Hit Any Issues**

- Check container logs for errors.
- Make sure you are editing files in `/home/micha/transcript-processor/nextjs-ui`.
- If hot reload fails, try restarting Docker Desktop or your WSL2 instance.

---

**You are now ready for a smooth, modern dev workflow!**

---

# About `WATCHPACK_POLLING=true` and Hot Reload in Docker

---

## What You Saw on YouTube

- The script:
  ```json
  "scripts": {
    "start": "react-scripts start",
    "start-watch": "WATCHPACK_POLLING=true react-scripts start",
    ...
  }
  ```
- This is for **Create React App** (CRA), not Next.js.
- `WATCHPACK_POLLING=true` forces the file watcher to use polling, which is more reliable in Docker/WSL2 environments where file system events may not propagate correctly.

---

## Does This Apply to Next.js?

- **Yes, you can use polling in Next.js too!**
- For Next.js, set the environment variable `WATCHPACK_POLLING=true` when starting the dev server:
  ```json
  "scripts": {
    "dev": "WATCHPACK_POLLING=true next dev",
    ...
  }
  ```
- Or, in Docker Compose:
  ```yaml
  command: sh -c "WATCHPACK_POLLING=true npx next dev"
  ```

---

## Why This Helps

- Polling mode makes file watching more reliable in Docker/WSL2, at the cost of slightly higher CPU usage.
- This often fixes hot reload issues when editing files from Windows or in certain Docker setups.

---

## What To Do

1. **Update your `package.json` in `nextjs-ui`:**
   ```json
   "scripts": {
     "dev": "WATCHPACK_POLLING=true next dev",
     ...
   }
   ```
2. **Or update your Docker Compose for `nextjs-ui`:**
   ```yaml
   command: sh -c "WATCHPACK_POLLING=true npx next dev"
   ```

---

**Summary:**  
- Setting `WATCHPACK_POLLING=true` is a valid and common fix for hot reload issues in Docker/WSL2 with Next.js or React.
- It is safe to try and often resolves file watching problems.

---

# Should You Set WATCHPACK_POLLING=true in package.json or docker-compose.yml?

---

## **Option 1: Set in `package.json`**

```json
// nextjs-ui/package.json
"scripts": {
  "dev": "WATCHPACK_POLLING=true next dev",
  // ...other scripts...
}
```

**Pros:**
- Works for anyone running `npm run dev` (locally or in Docker).
- Keeps the polling config close to your app code.
- No need to remember to set it in Docker Compose or other environments.

**Cons:**
- If you have different environments (dev, prod, CI), you may want polling only in Docker/WSL2, not everywhere.
- Less flexible if you want to override for specific environments.

---

## **Option 2: Set in `docker-compose.yml`**

```yaml
# docker-compose.yml for nextjs-ui service
command: sh -c "WATCHPACK_POLLING=true npx next dev"
```

**Pros:**
- Only applies polling when running in Docker Compose (not for local dev or CI).
- Keeps your `package.json` clean and generic.
- Easy to change or override for different environments.

**Cons:**
- If someone runs `npm run dev` outside Docker, polling is not enabled (could cause hot reload issues if not in Docker).
- Slightly more complex if you want to support both Docker and local dev with polling.

---

## **Summary Table**

| Approach         | Applies To         | Pros                        | Cons                        |
|------------------|-------------------|-----------------------------|-----------------------------|
| package.json     | All environments  | Simple, always works        | May poll when not needed    |
| docker-compose   | Docker only       | Flexible, env-specific      | Not for local `npm run dev` |

---

## **Best Practice for Your Project**

- **If you ONLY use Docker Compose to run Next.js:**  
  Set `WATCHPACK_POLLING=true` in `docker-compose.yml` (`command:`).
- **If you sometimes run `npm run dev` locally (outside Docker):**  
  Set it in `package.json` so it always works.

**You can also do both for maximum reliability.**

---

**Bottom line:**  
- Use `docker-compose.yml` for Docker-specific polling.
- Use `package.json` if you want polling everywhere.
- Both are valid; choose based on your workflow.

---

# How to Get Past Hot Reload/File Sync Delays as a Solo Dev

---

## 1. **Edit Only in the Directory Mapped to Docker**

- Make sure you are editing files in `/home/micha/transcript-processor/nextjs-ui` (WSL2), not on your Windows drive.
- Open your project in VS Code using the "Remote - WSL" extension and confirm your path is `/home/micha/...`.

---

## 2. **Use Polling for File Watching**

- In your `docker-compose.yml` for `nextjs-ui`, set:
  ```yaml
  command: sh -c "WATCHPACK_POLLING=true npx next dev"
  ```
- Or, in `package.json`:
  ```json
  "scripts": {
    "dev": "WATCHPACK_POLLING=true next dev",
    ...
  }
  ```

---

## 3. **Automate Dependency Installs**

- Use the `entrypoint.sh` script as previously provided to auto-install `node_modules` if missing.
- This avoids manual `npm install` steps.

---

## 4. **Restart Only the Next.js Container When Needed**

- You do **not** need to rebuild the whole project for every change.
- If hot reload fails, just restart the Next.js container:
  ```sh
  docker-compose restart nextjs-ui
  ```

---

## 5. **Summary Table**

| Step                        | Action/Command                                      |
|-----------------------------|----------------------------------------------------|
| Edit files                  | In `/home/micha/transcript-processor/nextjs-ui`    |
| Use polling                 | `WATCHPACK_POLLING=true` in compose or package.json|
| Auto-install deps           | Use `entrypoint.sh`                                |
| Restart Next.js only        | `docker-compose restart nextjs-ui`                 |

---

**As a solo dev, this setup will minimize delays and let you iterate quickly.  
If you still see delays, try smaller code changes and save often to trigger hot reload.**

If you want a one-liner to restart just the Next.js container, use:
```sh
docker-compose restart nextjs-ui
```
