import { cp, mkdir, rm } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');
const srcDir = path.join(rootDir, 'src');
const distDir = path.join(rootDir, 'dist');

await rm(distDir, { force: true, recursive: true });
await mkdir(distDir, { recursive: true });
await cp(srcDir, path.join(distDir, 'src'), { recursive: true });
await cp(path.join(rootDir, 'package.json'), path.join(distDir, 'package.json'));

console.log(`Build complete: ${distDir}`);
