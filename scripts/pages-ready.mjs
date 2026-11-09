import { writeFile } from 'node:fs/promises';
await writeFile(new URL('../docs/.nojekyll',import.meta.url),'');
console.log('GitHub Pages files are ready in docs/. Commit docs/ with your source changes.');
