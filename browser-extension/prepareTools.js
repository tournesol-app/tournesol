import { writeFile, mkdir, readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';

export const selectValue = (key, options) => {
  const result = options[key];
  if (result === undefined) {
    throw new Error(`No value found for the key ${JSON.stringify(key)}`);
  }
  return result;
};

export const generateImportWrappers = async (
  manifest,
  webAccessibleResources
) => {
  await Promise.all(
    manifest['content_scripts'].map(async (contentScript) => {
      await Promise.all(
        contentScript.js.map(async (js, i) => {
          const content = `import(chrome.runtime.getURL('../${js}'));\n`;
          const newJs = join('importWrappers', js);
          const path = join('src', newJs);
          await mkdir(dirname(path), { recursive: true });
          await writeFile(path, content);
          contentScript.js[i] = newJs;
          webAccessibleResources.push(js);
        })
      );
    })
  );
};

export const writeManifest = async (manifest, outputPath) => {
  const content = JSON.stringify(manifest, null, 2);
  await writeFile(outputPath, content);
};

export const writeConfig = async (config, outputPath) => {
  let content = '';
  for (let [key, value] of Object.entries(config)) {
    content += `export const ${key} = ${JSON.stringify(value)};\n`;
  }
  await writeFile(outputPath, content);
};

export const readPackage = async () => {
  const packageContent = await readFile('package.json');
  return JSON.parse(packageContent);
};
