describe('Settings - account page', () => {
  describe('Update email address flow', () => {
    before(() => {
      cy.recreateUser("test-email-update", "email1@example.com", "tournesol");
    })

    it('can update email', () => {
      cy.visit('/settings/account');
      cy.focused().type('test-email-update');
      cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
      cy.location('pathname').should('equal', '/settings/account');
      cy.contains('Your current email address is email1@example.com').should('be.visible');
      cy.get('input[name=email]').type('email2@example.com').type('{enter}');
      cy.contains('verification email has been sent ').should('be.visible');
      cy.getEmailLink().then(verifyLink => cy.visit(verifyLink));
      cy.contains('new email address is now verified').should('be.visible');
      cy.visit('/settings/account');
      cy.contains('Your current email address is email2@example.com').should('be.visible');
    })
  });

  describe('Check email status', () => {
    before(() => {
      cy.sql("DELETE FROM core_emaildomain where domain='@domain.test'");
      cy.recreateUser("test-email-status", "test-email-status@domain.test", "tournesol");
    })

    it('shows email trust status', () => {
      cy.visit('/settings/account');
      cy.focused().type('test-email-status');
      cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
      cy.contains(/Email status:.?Non-trusted/).should('be.visible');

      // Update email domain status
      cy.sql("UPDATE core_emaildomain SET status='ACK' WHERE domain = '@domain.test';")
      cy.reload();
      cy.contains(/Email status:.?Trusted/).should('be.visible');
    })
  })

  describe('Change password flow', () => {
    const username = 'nobody';
    const email = 'mr@nobody.org';
    const oldPassword = 'password'

    before(() => {
      cy.recreateUser(username, email, oldPassword);
    })

    it('can update password', () => {
      const newPaswsword = 'new_password';

      cy.visit('/settings/account');
      cy.focused().type(username);
      cy.get('input[name="password"]').click().type(oldPassword).type('{enter}');
      cy.location('pathname').should('equal', '/settings/account');

      cy.contains('Change password').should('be.visible');
      cy.get('input[name=old_password]').type(oldPassword);
      cy.get('input[name=password]').type(newPaswsword);
      cy.get('input[name=password_confirm]').type(newPaswsword).type('{enter}');
      cy.contains('Password changed successfully');

      cy.contains('Logout').click();
      cy.focused().type(username);

      // old password must not work anymore
      cy.get('input[name="password"]').click().type(oldPassword).type('{enter}');
      cy.location('pathname').should('equal', '/login');
      cy.contains('Invalid credentials given.');

      // only new password must work
      cy.get('input[name="password"]').click().clear().type(newPaswsword).type('{enter}');
      cy.location('pathname').should('equal', '/settings/account');
      cy.contains('Forgot password?').should('not.exist');
    })
  });
});
