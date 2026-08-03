import { readFile, writeFile } from 'node:fs/promises';
import { defineConfig } from 'i18next-cli';
import packageJson from './package.json' with { type: 'json' };

const supportedLanguageCodes = packageJson.config.supported_languages.map(
  (language) => language.code
);

// i18next-cli serializes catalogs with plain JSON.stringify, which writes
// non-breaking spaces as raw bytes indistinguishable from normal spaces in an
// editor. Re-escape them so they stay visible and hard to lose in review, as
// the previous i18next-parser tooling did.
const escapeNonBreakingSpaces = {
  name: 'escape-non-breaking-spaces',
  async afterSync(results) {
    for (const result of results) {
      if (!result.updated) continue;
      const content = await readFile(result.path, 'utf-8');
      if (!content.includes('\u00a0')) continue;
      await writeFile(result.path, content.replaceAll('\u00a0', '\\u00a0'));
    }
  },
};

export default defineConfig({
  locales: supportedLanguageCodes,
  extract: {
    input: ['src/**/*.{ts,tsx}'],
    ignore: ['src/services/**'],
    output: 'public/locales/{{language}}/{{namespace}}.json',
    defaultNS: 'translation',
    nsSeparator: ':',
    keySeparator: '.',
    contextSeparator: '_',
    pluralSeparator: '_',
    indentation: 2,
    sort: false,
    defaultValue: '',
    functions: ['t', '*.t'],
    transComponents: ['Trans'],
  },
  plugins: [escapeNonBreakingSpaces],
});
