describe('Signup', () => {
  before(() => {
    cy.sql("DELETE FROM core_user where username = 'test-register'");
  })

  it('user can create account', () => {
    cy.visit('/');
    cy.contains('Join us').click();
    cy.location('pathname').should('equal', '/signup');
    cy.get('input[name=email]').type('user@example.com');
    cy.get('input[name=username]').type('test-register');
    cy.get('input[name=password]').type('tourne50l');
    cy.get('input[name=password_confirm]').type('tourne50l');
    // Agree to the privacy policy
    cy.get('form input[type=checkbox]').check();
    cy.contains('Sign up').click();
    cy.contains('verification link').should('be.visible');
    cy.getEmailLink().then(verificationLink => cy.visit(verificationLink));
    cy.contains('account is now verified').should('be.visible');
    // Ensure that no other verification request is executed.
    cy.wait(500);
    cy.contains('Verification failed').should('not.exist');
  })
})
