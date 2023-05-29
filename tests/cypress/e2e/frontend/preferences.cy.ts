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

  it('Rate later setting', () => {
    cy.visit('/rate_later');
    cy.focused().type("blankuser");
    cy.get('input[name="password"]').click().type("tournesol").type('{enter}');
    cy.contains('removed after 4 comparison(s)').should('be.visible');

    cy.visit('/settings/preferences');
    cy.contains('Automatic removal').click().type('{selectAll}1');
    cy.contains('Update preferences').click();
    cy.visit('/rate_later');
    cy.get('input[placeholder="Video ID or URL"]').type('dQw4w9WgXcQ').type('{enter}');
    cy.visit('/comparison?uidA=yt%3AdQw4w9WgXcQ&uidB=yt%3APayvWj2piKg');
    cy.get('button').contains('submit').click();
    cy.visit('/rate_later');
    cy.contains('Your rate-later list contains 0 videos').should('be.visible');
  });
});