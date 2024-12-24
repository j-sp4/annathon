import fs from 'fs';
import path from 'path';
import os from 'os';

export function getAuthToken(configPath?: string): string {
  const configFile = configPath || path.join(os.homedir(), '.nugraph', 'config.json');

  if (fs.existsSync(configFile)) {
    const config = JSON.parse(fs.readFileSync(configFile, 'utf-8'));
    if (config.authToken) {
      return config.authToken;
    }
  }

  if (process.env.NUGRAPH_AUTH_TOKEN) {
    return process.env.NUGRAPH_AUTH_TOKEN;
  }

  throw new Error('Authentication token not found. Please authenticate using "nugraph auth".');
} 