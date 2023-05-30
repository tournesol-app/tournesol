describe("Settings - preferences page", () => {
  before(() => {
    cy.recreateUser("blankuser", "blankuser@preferences.test", "tournesol");
  });

  describe("Setting - display weekly collective goal", () => {
    it('Show weekly collective goal', () => { 
      cy.visit('/settings/preferences');
      cy.focused().type("blankuser");
      cy.get('input[name="password"]').click().type("tournesol").type('{enter}');
      cy.get('#videos_comparison_ui__weekly_collective_goal_display');
      cy.visit('/comparison');
      cy.contains('Weekly collective goal').should('be.visible');
      cy.visit('/comparison?embed=1');
      cy.contains('Weekly collective goal').should('be.visible');
    });
  
    it('Show weekly collective goal', () => { 
      cy.visit('/settings/preferences');
      cy.focused().type("blankuser");
      cy.get('input[name="password"]').click().type("tournesol").type('{enter}');
      cy.get('#videos_comparison_ui__weekly_collective_goal_display').click();
      cy.get('[data-value="WEBSITE_ONLY"]').click();
      cy.contains('Update preferences').click();
      cy.visit('/comparison');
      cy.contains('Weekly collective goal').should('be.visible');
      cy.visit('/comparison?embed=1');
      cy.contains('Weekly collective goal').should('not.exist');
  
    });

    it('Show weekly collective goal', () => { 
      cy.visit('/settings/preferences');
      cy.focused().type("blankuser");
      cy.get('input[name="password"]').click().type("tournesol").type('{enter}');
      cy.get('#videos_comparison_ui__weekly_collective_goal_display').click();
      cy.get('[data-value="EMBEDDED_ONLY"]').click();
      cy.contains('Update preferences').click();
      cy.visit('/comparison');
      cy.contains('Weekly collective goal').should('not.exist');
      cy.visit('/comparison?embed=1');
      cy.contains('Weekly collective goal').should('be.visible');
    });

    it('Show weekly collective goal', () => { 
      cy.visit('/settings/preferences');
      cy.focused().type("blankuser");
      cy.get('input[name="password"]').click().type("tournesol").type('{enter}');
      cy.get('#videos_comparison_ui__weekly_collective_goal_display').click();
      cy.get('[data-value="NEVER"]').click();
      cy.contains('Update preferences').click();
      cy.visit('/comparison');
      cy.contains('Weekly collective goal').should('not.exist');
      cy.visit('/comparison?embed=1');
      cy.contains('Weekly collective goal').should('not.exist');
    });
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
    cy.contains('removed after 1 comparison(s)').should('be.visible');
    cy.get('input[placeholder="Video ID or URL"]').type('dQw4w9WgXcQ').type('{enter}');
    cy.visit('/comparison?uidA=yt%3AdQw4w9WgXcQ&uidB=yt%3APayvWj2piKg');
    cy.get('button').contains('submit').click();
    cy.visit('/rate_later');
    cy.contains('Your rate-later list contains 0 videos').should('be.visible');
  });

});