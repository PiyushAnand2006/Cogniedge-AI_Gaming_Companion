# CogniEdge Windows Deployment & Packaging Guide

---

## 1. Development Mode

To run all subsystems in parallel:

```bash
# Terminal 1: Python FastAPI Service & Performance Collector
cd cogniedge/services
python ai_service.py

# Terminal 2: Next.js Frontend
cd cogniedge
npm run dev

# Terminal 3: Optional Electron Desktop Shell
cd cogniedge
npm run electron
```

---

## 2. Production Build

To build the production Next.js desktop bundle:

```bash
cd cogniedge
npm run build
```

---

## 3. Creating Windows Executable (`.exe`)

```bash
cd cogniedge
npm run dist
```
Generates NSIS installer and standalone portable zip under `cogniedge/dist/`.
The Electron shell automatically handles Python backend initialization and child process cleanup upon application shutdown.
