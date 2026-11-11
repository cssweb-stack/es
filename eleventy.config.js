import { project, sharedModule } from './scripts/shared-bootstrap.mjs';
const { configureUnitSite } = await import(sharedModule('scripts/unit-site/eleventy.mjs'));
export default config => configureUnitSite(config, project);
