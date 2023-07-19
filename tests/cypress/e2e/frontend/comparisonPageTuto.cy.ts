describe('Comparison page tutorial', () => {
  const username = "test-comparison-tutorial";

  before(() => {
    cy.recreateUser(username, "test-comparison-tutorial@example.com", "tournesol");
  });

  describe('collective goal', () => {
    it('is not displayed during tutorial', () => {
      cy.visit('/comparison');
      cy.focused().type(username);
      cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
      cy.contains('Weekly collective goal').should('not.exist');
    })
  });
});
  