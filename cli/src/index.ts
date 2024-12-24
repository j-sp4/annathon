#!/usr/bin/env node

import { Command } from 'commander';
import dotenv from 'dotenv';
import { authenticate } from './auth';
import { uploadFile } from './upload';
import { indexFiles } from './indexFiles';
import { searchQuery } from './search';

// Load environment variables from .env file
dotenv.config();

const program = new Command();

program
  .name('nugraph')
  .description('CLI tool for nugraph')
  .version('1.0.0');

program
  .command('auth')
  .description('Authenticates the user with the backend service')
  .option('-u, --username <USERNAME>', 'The username for authentication')
  .option('-p, --password <PASSWORD>', 'The password for authentication')
  .option('--config <FILE>', 'Custom configuration file path')
  .action(async (options) => {
    await authenticate(options.username, options.password, options.config);
  });

program
  .command('upload <file_path>')
  .description('Uploads a single local file to the storage bucket and registers it with the backend')
  .option('--auth-token <TOKEN>', 'Provide an auth token directly, overriding stored token')
  .option('--output <FORMAT>', 'Output format (e.g., json, text). Defaults to text')
  .action(async (filePath, options) => {
    await uploadFile(filePath, options.authToken, options.output);
  });

program
  .command('index [file_paths...]')
  .description('Uploads multiple local files at once and indexes them with the backend')
  .option('--file <FILE>', 'A file containing a list of local file paths')
  .option('--auth-token <TOKEN>', 'Provide an auth token directly, overriding stored token')
  .option('--output <FORMAT>', 'Output format (e.g., json, text). Defaults to text')
  .action(async (filePaths, options) => {
    await indexFiles(filePaths, options.file, options.authToken, options.output);
  });

program
  .command('search <query_string>')
  .description('Searches the indexed documents using a query string')
  .option('--auth-token <TOKEN>', 'Provide an auth token directly, overriding stored token')
  .option('--limit <N>', 'Limit the number of results')
  .option('--output <FORMAT>', 'Output format (e.g., json, text). Defaults to text')
  .action(async (queryString, options) => {
    await searchQuery(queryString, options.authToken, options.limit, options.output);
  });

program.parse(process.argv); 