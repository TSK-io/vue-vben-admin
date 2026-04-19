import { appendFile, mkdir } from 'node:fs/promises';
import path from 'node:path';

const auditDir = path.resolve(process.cwd(), 'logs');
const auditFile = path.join(auditDir, 'audit.log');

export async function writeAuditLog(entry) {
  await mkdir(auditDir, { recursive: true });
  await appendFile(auditFile, `${JSON.stringify(entry)}\n`, 'utf8');
}
