// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })

Cypress.Commands.add('sql', (query) =>
  cy.exec(`docker exec tournesol-dev-db psql -U tournesol -c "${query}"`)
)

Cypress.Commands.add('getEmailLink', () =>
  cy.exec('docker logs tournesol-dev-api --since=1m 2>&1 | grep "http://127.0.0.1:3000" | tail -1')
    .then(result => {
      const link = result.stdout;
      // Cypress requires to visit a single origin, and the email contains 127.0.0.1 instead of localhost.
      return link.replace('127.0.0.1', 'localhost');
    })
)
