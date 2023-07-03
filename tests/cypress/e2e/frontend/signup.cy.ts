describe('Signup', () => {

  beforeEach(() => {
    cy.sql("DELETE FROM oauth2_provider_refreshtoken");
    cy.sql("DELETE FROM oauth2_provider_accesstoken");
    cy.sql("DELETE FROM core_user where username = 'test-register'");
  });

  it('allows users to create an account', () => {
    cy.visit('/');
    cy.contains('Join us').click();
    cy.location('pathname').should('equal', '/signup');

    cy.get('input[name=email]').type('user@example.com');
    cy.get('input[name=username]').type('test-register');
    cy.get('input[name=password]').type('tourne50l');
    cy.get('input[name=password_confirm]').type('tourne50l');
    cy.get('input[name=accept_terms]').check();

    cy.contains('Sign up').click();
    cy.contains('verification link').should('be.visible');
    cy.getEmailLink().then(verificationLink => cy.visit(verificationLink));
    cy.contains('account is now verified').should('be.visible');
    // Ensure that no other verification request is executed.
    cy.wait(500);
    cy.contains('Verification failed').should('not.exist');
  });

  it('allows users to define their notification preferences', () => {
    cy.visit('/');
    cy.contains('Join us').click();
    cy.location('pathname').should('equal', '/signup');

    cy.get('input[name=email]').type('user@example.com');
    cy.get('input[name=username]').type('test-register');
    cy.get('input[name=password]').type('tourne50l');
    cy.get('input[name=password_confirm]').type('tourne50l');
    cy.get('form input[name=accept_terms]').check();

    // [GIVEN] the notification "research" is selected
    cy.get('input[name=notifications_email__research]').check();

    cy.contains('Sign up').click();
    cy.getEmailLink().then(verificationLink => cy.visit(verificationLink));

    // [WHEN] the user goes to its preference page
    cy.contains('Log in').click();
    cy.focused().type('test-register');
    cy.get('input[name="password"]').click().type('tourne50l').type('{enter}');
    cy.wait(500);
    cy.visit('/settings/preferences');

    // [THEN] only the selected notifications are checked
    cy.get('input[name=notifications_email__research]').should('be.checked');
    cy.get('input[name=notifications_email__new_features]').should('not.be.checked');
  });
});
