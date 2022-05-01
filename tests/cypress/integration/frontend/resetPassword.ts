describe('Password reset', () => {
  beforeEach(() => {
    cy.recreateUser("username-pwreset", "test@example.com", "forgottenPassword");
  });

  ["username-pwreset", "test@example.com"].forEach(login => {
    it(`can reset password for ${login}`, () => {
      cy.visit('/login');
      cy.contains('Forgot').click();
      cy.location('pathname').should('equal', '/forgot');
      cy.get('input[name=login]').type(login).type('{enter}');
      cy.contains('email will be sent').should('be.visible');
      cy.getEmailLink().then(resetLink => cy.visit(resetLink));
      cy.contains('New password').should('be.visible');
      cy.get('input[name=password]').type('tournesol-new-password');
      cy.get('input[name=confirm_password]').type('tournesol-new-password').type('{enter}');
      cy.contains('password has been modified').should('be.visible');
      cy.location('pathname').should('equal', '/login');
      // Login with the new password
      cy.get('input[name=username]').type('username-pwreset');
      cy.get('input[name=password]').type('tournesol-new-password').type('{enter}');
      cy.contains('a[href="/settings/profile"]', 'username-pwreset').should('be.visible');
    })
  });
})
