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
  cy.exec('docker logs tournesol-dev-api --since=10s 2>&1 | grep "http://localhost:3000" | tail -1')
    .then(result => result.stdout)
)

Cypress.Commands.add('recreateUser', (username, email, password) =>
  cy.exec(`docker exec tournesol-dev-api python manage.py shell --command="
from core.models import User
User.objects.filter(username='${username}').delete()
User.objects.create_user(username='${username}', email='${email}', password='${password}')
"`)
)
