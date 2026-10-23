/// <reference types="cypress" />
// ***********************************************************
// This example plugins/index.js can be used to load plugins
//
// You can change the location of this file or turn off loading
// the plugins file with the 'pluginsFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/plugins-guide
// ***********************************************************

// This function is called when a project is opened or re-opened (e.g. due to
// the project's config changing)

const child_process = require("child_process")
const fs = require('fs');
const path = require('path');

/**
 * @type {Cypress.PluginConfig}
 */
// eslint-disable-next-line no-unused-vars
module.exports = (on, config) => {
  // `on` is used to hook into various events Cypress emits
  // `config` is the resolved Cypress config

  on('before:browser:launch', (browser, launchOptions) => {
    const browserSrc = path.join(__dirname, '../../../browser-extension/src')
    if (fs.existsSync(path.join(browserSrc, 'manifest.json'))) {
      launchOptions.extensions.push(browserSrc);
    }
    launchOptions.env.LANGUAGE = "en"
    return launchOptions
  })

  on('task', {
    exec({ cmd, cwd = process.cwd(), env = {}, timeout = 60_000 }) {
      return new Promise((resolve) => {
        child_process.exec(
          cmd,
          { cwd, env: { ...process.env, ...env }, timeout },
          (err, stdout, stderr) =>
            resolve({ exitCode: err ? (err.code ?? 1) : 0, stdout, stderr })
        )
      })
    },
  })
}
