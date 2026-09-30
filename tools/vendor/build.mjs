// Bundles GSAP and a Three.js subset into classic IIFE scripts for templates/.
// Run: npm ci && node build.mjs  (from tools/vendor). Page builds only read the output files.
import { build } from 'esbuild';
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const skill = join(here, '..', '..');
const pkg = (name) => JSON.parse(readFileSync(join(here, 'node_modules', name, 'package.json'), 'utf8'));

const targets = [
  { name: 'gsap', entry: 'gsap-entry.js', out: 'templates/vendor/gsap.js', pkg: 'gsap', license: 'https://gsap.com/standard-license' },
  { name: 'three', entry: 'three-entry.js', out: 'templates/sections/_shared/three.js', pkg: 'three', license: 'MIT, https://github.com/mrdoob/three.js/blob/dev/LICENSE' }
];

const versions = {};
for (const t of targets) {
  const version = pkg(t.pkg).version;
  const result = await build({
    entryPoints: [join(here, t.entry)],
    bundle: true,
    format: 'iife',
    minify: true,
    target: 'es2019',
    charset: 'ascii',
    legalComments: 'none',
    write: false
  });
  const banner = `/* ${t.pkg} ${version}, ${t.license}. Built by tools/vendor/build.mjs, do not edit. */\n`;
  const text = banner + result.outputFiles[0].text;
  const out = join(skill, t.out);
  writeFileSync(out, text);
  versions[t.name] = {
    package: t.pkg,
    version,
    license: t.license,
    file: t.out,
    bytes: Buffer.byteLength(text),
    sha256: createHash('sha256').update(text).digest('hex')
  };
  console.log(`${t.out}  ${(Buffer.byteLength(text) / 1024).toFixed(1)} KB`);
}
writeFileSync(join(skill, 'templates', 'vendor', 'VERSIONS.json'), JSON.stringify(versions, null, 2) + '\n');
