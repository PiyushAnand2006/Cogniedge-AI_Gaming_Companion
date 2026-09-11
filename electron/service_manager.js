/**
 * CogniEdge Electron Python Service Manager
 * Spawns, monitors health, and safely terminates the local Python FastAPI backend service.
 */

const { spawn } = require('child_process');
const path = require('path');
const http = require('http');

class ServiceManager {
  constructor() {
    this.pythonProcess = null;
    this.isShuttingDown = false;
  }

  startBackend() {
    const servicePath = path.join(__dirname, '../services/ai_service.py');
    const pythonExe = process.platform === 'win32' ? 'python' : 'python3';

    console.log(`[CogniEdge Electron] Launching Local AI Service: ${servicePath}`);

    this.pythonProcess = spawn(pythonExe, [servicePath], {
      cwd: path.dirname(servicePath),
      env: { ...process.env, PYTHONUNBUFFERED: '1' },
      stdio: ['ignore', 'pipe', 'pipe']
    });

    this.pythonProcess.stdout.on('data', (data) => {
      console.log(`[Python AI Service] ${data.toString().trim()}`);
    });

    this.pythonProcess.stderr.on('data', (data) => {
      console.error(`[Python AI Service ERR] ${data.toString().trim()}`);
    });

    this.pythonProcess.on('close', (code) => {
      if (!this.isShuttingDown) {
        console.warn(`[CogniEdge Electron] Python AI service exited with code ${code}. Restarting in 3s...`);
        setTimeout(() => this.startBackend(), 3000);
      }
    });
  }

  stopBackend() {
    this.isShuttingDown = true;
    if (this.pythonProcess) {
      console.log('[CogniEdge Electron] Terminating Python AI service...');
      this.pythonProcess.kill();
      this.pythonProcess = null;
    }
  }

  async waitForHealth(maxRetries = 20, intervalMs = 500) {
    for (let i = 0; i < maxRetries; i++) {
      try {
        const res = await new Promise((resolve, reject) => {
          http.get('http://127.0.0.1:8088/health', (res) => resolve(res.statusCode)).on('error', reject);
        });
        if (res === 200) {
          console.log('[CogniEdge Electron] Local AI Service is ONLINE.');
          return true;
        }
      } catch (e) {
        // Wait and retry
      }
      await new Promise(r => setTimeout(r, intervalMs));
    }
    console.warn('[CogniEdge Electron] Python backend health check timed out.');
    return false;
  }
}

module.exports = new ServiceManager();
