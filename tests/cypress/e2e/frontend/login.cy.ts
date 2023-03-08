describe('Login', () => {
  it('home page loads correctly', () => {
    cy.visit('/');
    cy.contains('Tournesol').should('be.visible');
  })

  it('can login and logout', () => {
    cy.visit('/');
    cy.contains('Log in').click();
    cy.location('pathname').should('equal', '/login')
    cy.focused().type('user');
    cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
    cy.location('pathname').should('equal', '/');
    cy.contains('Log in').should('not.exist');

    cy.get('button#personal-menu-button').click();
    cy.contains('Logout').should('be.visible');
  })

  it('can login with email and logout', () => {
    cy.visit('/');
    cy.contains('Log in').click();
    cy.location('pathname').should('equal', '/login');
    cy.focused().type('user1@tournesol.app');
    cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
    cy.location('pathname').should('equal', '/');
    cy.contains('.MuiToolbar-root', 'user1').should('be.visible');
    cy.contains('Log in').should('not.exist');

    cy.get('button#personal-menu-button').click();
    cy.get('#personal-menu').contains('Logout').click();

    cy.contains('Log in').should('be.visible');
  })

  it('can login with lower/upper email variant and logout', () => {
    cy.visit('/');
    cy.contains('Log in').click();
    cy.location('pathname').should('equal', '/login');
    cy.focused().type('USER1@tournesol.app');
    cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
    cy.location('pathname').should('equal', '/');
    cy.contains('.MuiToolbar-root', 'user1').should('be.visible');
    cy.contains('Log in').should('not.exist');

    cy.get('button#personal-menu-button').click();
    cy.get('#personal-menu').contains('Logout').click();

    cy.contains('Log in').should('be.visible');
  })
})
