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
const path = require('path');

/**
 * @type {Cypress.PluginConfig}
 */
// eslint-disable-next-line no-unused-vars
module.exports = (on, config) => {
  // `on` is used to hook into various events Cypress emits
  // `config` is the resolved Cypress config

  on('before:browser:launch', (browser, launchOptions) => {
    launchOptions.extensions.push(path.join(__dirname, '../../../browser-extension/src'));
    launchOptions.env.LANGUAGE = "en"
    return launchOptions
  })

  on('task', {
    execFile({ file, args = [] }) {
      return new Promise((resolve) => {
        child_process.execFile(
          file,
          args,
          { timeout: 60_000 },
          (err, stdout, stderr) => {
            resolve({ exitCode: err ? (err.code ?? 1) : 0, stdout, stderr })
          })
      })
    },
  })
}
