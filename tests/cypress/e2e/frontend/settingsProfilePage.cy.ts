describe('Settings - profile page', () => {
  describe('Change username flow', () => {
    const user1username = 'nobody';
    const user1NewUsername = 'noone';
    const user1email = 'user1@nobody.test';
    const user1password = 'user1password'

    const user2username = 'already';
    const user2email = 'user2@nobody.test';
    const user2password = 'user2password';

    beforeEach(() => {
      cy.deleteUser(user1NewUsername);
      cy.recreateUser(user1username, user1email, user1password);
      cy.recreateUser(user2username, user2email, user2password);
    })

    it('can change username', () => {
      cy.visit('/settings/profile');
      cy.focused().type(user1username);
      cy.get('input[name="password"]').click().type(user1password).type('{enter}');
      cy.location('pathname').should('equal', '/settings/profile');

      cy.contains('Profile').should('be.visible');
      cy.get('input[name=username]').should("have.value", user1username).clear();
      cy.get('input[name=username]').type(user1NewUsername).type('{enter}');
      cy.contains('Profile changed successfully');

      cy.get('button#personal-menu-button').click();
      cy.get('#personal-menu').contains('Logout').click();

      cy.focused().type(user1username);

      // old username must not work anymore
      cy.get('input[name="password"]').click().type(user1password).type('{enter}');
      cy.location('pathname').should('equal', '/login');
      cy.contains('Invalid credentials given.');

      // only new username must work
      cy.get('input[name="username"]').click().clear();
      cy.get('input[name="username"]').type(user1NewUsername).type('{enter}');
      cy.contains('Profile').should('be.visible');
      cy.location('pathname').should('equal', '/settings/profile');
      cy.contains('Forgot password?').should('not.exist');
      cy.get('input[name=username]').should('have.value', user1NewUsername);
    })

    it('cannot use username already taken', () => {
      cy.visit('/settings/profile');
      cy.focused().type(user1username);
      cy.get('input[name="password"]').click().type(user1password).type('{enter}');
      cy.location('pathname').should('equal', '/settings/profile');

      cy.contains('Profile').should('be.visible');
      cy.get('input[name=username]').should("have.value", user1username).clear();
      cy.get('input[name=username]').type(user2username).type('{enter}');
      cy.contains('A user with that username already exists.');

      cy.get('button#personal-menu-button').click();
      cy.get('#personal-menu').contains('Logout').click();

      cy.focused().type(user2username);

      // the desired username must not work (because already taken)
      cy.get('input[name="password"]').click().type(user1password).type('{enter}');
      cy.location('pathname').should('equal', '/login');
      cy.contains('Invalid credentials given.');

      // only the original username must work
      cy.get('input[name="username"]').click().clear().type(user1username).type('{enter}');
      cy.location('pathname').should('equal', '/settings/profile');
      cy.contains('Forgot password?').should('not.exist');
      cy.get('input[name=username]').should('have.value', user1username);
    })
  });
});
