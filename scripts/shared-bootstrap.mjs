import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
export const project = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const settings = JSON.parse(fs.readFileSync(path.join(project, 'shared.config.json'), 'utf8'));
export const sharedRoot = path.resolve(project, process.env.SHARED_SOURCE || settings.localPath);
export const sharedModule = relative => pathToFileURL(path.join(sharedRoot, relative)).href;
