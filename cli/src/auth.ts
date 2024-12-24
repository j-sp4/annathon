import axios from 'axios';
import fs from 'fs';
import path from 'path';
import os from 'os';

const API_URL = process.env.GRAPH_RAG_API_URL;

export async function authenticate(username: string, password: string, configPath?: string) {
  try {
    const response = await axios.post(`${API_URL}/auth`, { username, password });
    const token = response.data.token;

    const configFile = configPath || path.join(os.homedir(), '.nugraph', 'config.json');
    const configDir = path.dirname(configFile);

    if (!fs.existsSync(configDir)) {
      fs.mkdirSync(configDir, { recursive: true });
    }

    fs.writeFileSync(configFile, JSON.stringify({ authToken: token }, null, 2));

    console.log('Authentication successful. Token stored at:', configFile);
  } catch (error: any) {
    console.error('Authentication failed:', error.response?.data || error.message);
    process.exit(2);
  }
} 