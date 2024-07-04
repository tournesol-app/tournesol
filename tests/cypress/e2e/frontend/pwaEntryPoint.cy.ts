describe('PWA - entry point', () => {
  const username = "test-pwa-entry-point";

  beforeEach(() => {
    cy.recreateUser(username, `${username}@example.com`, "tournesol");
  });

  after(() => {
    cy.deleteUser(username);
  });

  const login = () => {
    cy.focused().type(username);
    cy.get('input[name="password"]').click().type("tournesol").type('{enter}');
  }

  describe('redirection', () => {
    it('anonymous users redirected to Top items', () => {
      cy.visit('/pwa/start');
      cy.location('pathname').should('equal', '/feed/top');
      cy.location('search').should('contain', '?date=Month');
    });

    it('authenticated users redirected to For you', () => {
      cy.visit('/settings/preferences');
      login();
      cy.contains('Update preferences').click();

      cy.visit('/pwa/start');
      cy.location('pathname').should('equal', '/feed/foryou');
    });
  });  
});
