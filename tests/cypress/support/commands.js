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

Cypress.Commands.add('execFile', (file, ...args) => cy.task('execFile', { file, args }))

Cypress.Commands.add('sql', (query) =>
  cy.execFile('docker', 'exec', 'tournesol-dev-db', 'psql', '-U', 'tournesol', '-c', query)
)

Cypress.Commands.add('getEmailLink', () =>
  cy.execFile('docker', 'logs', 'tournesol-dev-api', '--since=10s')
    .then(({ stdout }) =>
      stdout.split('\n')
        .map((line) => line.trim())
        .filter((line) => line.startsWith('http://localhost:3000'))
        .pop() ?? ''
    )
)

Cypress.Commands.add('recreateUser', (username, email, password) =>
  cy.execFile('docker', 'exec', 'tournesol-dev-api', 'uv', 'run', 'python', 'manage.py', 'shell', '--command', `
from core.models import User
User.objects.filter(username='${username}').delete()
User.objects.create_user(username='${username}', email='${email}', password='${password}')
`)
)

/**
 * Delete a user from the database.
 */
Cypress.Commands.add('deleteUser', (username) =>
  cy.execFile('docker', 'exec', 'tournesol-dev-api', 'uv', 'run', 'python', 'manage.py', 'shell', '--command', `
from core.models import User
User.objects.filter(username='${username}').delete()
`)
)

/**
 * Delete a single comparison made by a given user.
 */
Cypress.Commands.add('deleteOneComparisonOfUser', (username, uidA, uidB) => {
  cy.sql(`
    DELETE FROM tournesol_comparisoncriteriascore
    WHERE comparison_id = (
      SELECT id
      FROM tournesol_comparison
      WHERE entity_1_id = (
        SELECT id FROM tournesol_entity WHERE uid = '${uidA}'
      ) AND entity_2_id = (
        SELECT id FROM tournesol_entity WHERE uid = '${uidB}'
      ) AND user_id = (
        SELECT id FROM core_user WHERE username = '${username}'
      )
    );
  `);

  cy.sql(`
      DELETE FROM tournesol_comparison
          WHERE entity_1_id = (
              SELECT id FROM tournesol_entity WHERE uid = '${uidA}'
          ) AND entity_2_id = (
              SELECT id FROM tournesol_entity WHERE uid = '${uidB}'
          ) AND user_id = (
              SELECT id FROM core_user WHERE username = '${username}'
          );
    `);
});

/**
 * Delete all comparisons made by a given user.
 */
Cypress.Commands.add('deleteAllComparisonsOfUser', (username) => {
  cy.sql(`
    DELETE FROM tournesol_comparisoncriteriascore
    WHERE comparison_id IN (
        SELECT id
        FROM tournesol_comparison
        WHERE user_id = (
            SELECT id FROM core_user WHERE username = '${username}'
        )
    );
  `);

  cy.sql(`
    DELETE FROM tournesol_comparison
        WHERE user_id = (
            SELECT id FROM core_user WHERE username = '${username}'
        );
  `);
});
