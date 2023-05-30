describe('Settings - preferences page', () => {
  before(() => {
    cy.recreateUser("test-preferences-page", "test-preferences-page@example.com", "tournesol");
  });

  const login = () => {
    cy.focused().type('test-preferences-page');
    cy.get('input[name="password"]').click().type("tournesol").type('{enter}');
  }

  // describe('Navigation', () => {
  //   it('is accessible from the personal menu', () => {
  //     cy.visit('/login');
  //     login();

  //     cy.get('button#personal-menu-button').click();
  //     cy.get('#personal-menu').contains('Preferences').click();

  //     cy.location('pathname').should('equal', '/settings/preferences');
  //   });
  // });

  // describe('Setting - display weekly collective goal', () => {
  //   const fieldSelector = '#videos_comparison_ui__weekly_collective_goal_display';

  //   it('handles the value ALWAYS', () => {
  //     cy.visit('/settings/preferences');
  //     login();

  //     // Ensure the default value is ALWAYS
  //     cy.get(
  //       '[data-testid=videos_weekly_collective_goal_display]'
  //     ).should('have.value', 'ALWAYS');

  //     cy.visit('/comparison');
  //     cy.contains('Weekly collective goal').should('be.visible');
  //     cy.visit('/comparison?embed=1');
  //     cy.contains('Weekly collective goal').should('be.visible');
  //   });

  //   it('handles the value WEBSITE_ONLY', () => {
  //     cy.visit('/settings/preferences');
  //     login();

  //     cy.get(fieldSelector).click();
  //     cy.contains('Website only').click();
  //     cy.contains('Update preferences').click();

  //     cy.visit('/comparison');
  //     cy.contains('Weekly collective goal').should('be.visible');
  //     cy.visit('/comparison?embed=1');
  //     cy.contains('Weekly collective goal').should('not.exist');

  //   });

  //   it('handles the value EMBEDDED_ONLY', () => {
  //     cy.visit('/settings/preferences');
  //     login();

  //     cy.get(fieldSelector).click();
  //     cy.contains('Extension only').click();
  //     cy.contains('Update preferences').click();

  //     cy.visit('/comparison');
  //     cy.contains('Weekly collective goal').should('not.exist');
  //     cy.visit('/comparison?embed=1');
  //     cy.contains('Weekly collective goal').should('be.visible');
  //   });

  //   it('handles the value NEVER', () => {
  //     cy.visit('/settings/preferences');
  //     login();

  //     cy.get(fieldSelector).click();
  //     cy.contains('Never').click();
  //     cy.contains('Update preferences').click();

  //     cy.visit('/comparison');
  //     cy.contains('Weekly collective goal').should('not.exist');
  //     cy.visit('/comparison?embed=1');
  //     cy.contains('Weekly collective goal').should('not.exist');
  //   });
  // });

  describe('Setting - rate-later auto removal', () => {
    it('handles changing the value', () => {
      cy.visit('/rate_later');
      login();

      cy.contains('removed after 4 comparison(s)').should('be.visible');

      cy.get('a[aria-label="Link to the preferences page"]').click();
      cy.contains('Automatic removal').click().type('{selectAll}1');
      cy.contains('Update preferences').click();

      cy.visit('/rate_later');
      cy.contains('removed after 1 comparison(s)').should('be.visible');

      cy.get('input[placeholder="Video ID or URL"]').type('nffV2ZuEy_M').type('{enter}');
      cy.contains('Your rate-later list contains 1 video').should('be.visible');

      cy.visit('/comparison?uidA=yt%3AnffV2ZuEy_M&uidB=yt%3AdQw4w9WgXcQ');
      cy.get('button').contains('submit').click();
      cy.visit('/rate_later');
      cy.contains('Your rate-later list contains 0 videos').should('be.visible');
    });
  });
});
