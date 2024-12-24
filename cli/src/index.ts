#!/usr/bin/env node
import path from 'path';
import dotenv from 'dotenv';
// Load environment variables from .env file
dotenv.config({ path: path.resolve(__dirname, '../.env') });

import { Command } from 'commander';
import { authenticate } from './auth';
import { uploadFile } from './upload';
import { indexFiles } from './indexFiles';
import { searchQuery } from './search';


const program = new Command();

program
  .name('nugraph')
  .description('CLI tool for nugraph')
  .version('1.0.0');

// program
//   .command('auth')
//   .description('Authenticates the user with the backend service')
//   .option('-u, --username <USERNAME>', 'The username for authentication')
//   .option('-p, --password <PASSWORD>', 'The password for authentication')
//   .option('--config <FILE>', 'Custom configuration file path')
//   .action(async (options) => {
//     await authenticate(options.username, options.password, options.config);
//   });

program
  .command('index [file_paths...]')
  .description('Uploads multiple local files at once and indexes them with the backend')
  .action(async (filePaths) => {
    await indexFiles(filePaths);
  });

program
  .command('search <query_string>')
  .description('Searches the indexed documents using a query string')
  .action(async (queryString) => {
    await searchQuery(queryString);
  });

program.parse(process.argv); 