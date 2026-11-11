import { project, sharedModule } from './shared-bootstrap.mjs';
const { createSharedSource } = await import(sharedModule('scripts/unit-site/shared-source.mjs'));
console.log('Shared source ready: ' + createSharedSource(project).checkShared());
