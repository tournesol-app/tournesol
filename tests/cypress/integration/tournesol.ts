describe('Tournesol basic tests', () => {
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
    cy.url().should('match', /\/$/);
    cy.contains('Log in').should('not.exist');
    cy.contains('Logout').click();
    cy.contains('Log in').should('be.visible');
  })
})


describe('Rate later list', () => {
  before(() => {
    cy.sql("TRUNCATE tournesol_videoratelater");
  })

  it('can add video to rate later list', () => {
    cy.visit('/rate_later');
    cy.url().should('include', '/login');
    cy.focused().type('user');
    cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
    cy.contains('0 video').should('be.visible');
    cy.get('input[placeholder="Video id or URL"]').type('dQw4w9WgXcQ').type('{enter}');
    cy.contains('1 video').should('be.visible');
  })
})


describe('Account creation', () => {
  before(() => {
    cy.sql("DELETE FROM core_user where username = 'test-user'");
  })

  it('can create account', () => {
    cy.visit('/');
    cy.contains('Join us').click();
    cy.url().should('contain', '/signup');
    cy.get('input[name=email]').type('user@example.com');
    cy.get('input[name=username]').type('test-user');
    cy.get('input[name=password]').type('tourne50l');
    cy.get('input[name=password_confirm]').type('tourne50l');
    // Agree to the privacy policy
    cy.get('form input[type=checkbox]').check();
    cy.contains('Sign up').click();
    cy.contains('verification link').should('be.visible');
    cy.getEmailLink().then(verificationLink => cy.visit(verificationLink));
    cy.contains('account is now verified').should('be.visible');
  })
})