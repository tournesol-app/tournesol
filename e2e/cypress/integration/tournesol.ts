const baseUrl = Cypress.config('baseUrl');

describe('Tournesol home page', () => {
  it('loads correctly', () => {
    cy.visit('/');
    cy.contains('Tournesol').should('be.visible');
  })

  it('can login and logout', () => {
    cy.visit('/');
    cy.contains('Log in').click();
    cy.url().should('include', '/login')
    cy.focused().type('user');
    cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
    cy.url().should('equal', `${baseUrl}/`);
    cy.contains('Logout').click();
    cy.contains('Log in').should('be.visible')
  })
})
