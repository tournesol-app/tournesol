describe("My user's preferences", () => {
  before(() => {
    cy.recreateUser("blankuser", "blankuser@preferences.test", "tournesol");
  });

  it('Show weekly collective goal', () => {
    cy.visit('/settings/preferences');
    cy.focused().type("blankuser");
    cy.get('input[name="password"]').click().type("tournesol").type('{enter}');
    cy.contains('Always').should('be.visible');
    cy.visit('/comparison');
    cy.contains('Weekly collective goal').should('be.visible');
    cy.visit('/comparison?embed=1');
    cy.contains('Weekly collective goal').should('be.visible');

    cy.visit('/settings/preferences');
    cy.contains('Always').click();
    cy.contains('Website only').click();
    cy.contains('Update preferences').click();
    cy.visit('/comparison');
    cy.contains('Weekly collective goal').should('be.visible');
    cy.visit('/comparison?embed=1');
    cy.contains('Weekly collective goal').should('not.exist');

    cy.visit('/settings/preferences');
    cy.contains('Website only').click();
    cy.contains('Extension only').click();
    cy.contains('Update preferences').click();
    cy.visit('/comparison');
    cy.contains('Weekly collective goal').should('not.exist');
    cy.visit('/comparison?embed=1');
    cy.contains('Weekly collective goal').should('be.visible');

    cy.visit('/settings/preferences');
    cy.contains('Extension only').click();
    cy.contains('Never').click();
    cy.contains('Update preferences').click();
    cy.visit('/comparison');
    cy.contains('Weekly collective goal').should('not.exist');
    cy.visit('/comparison?embed=1');
    cy.contains('Weekly collective goal').should('not.exist');
  });
});