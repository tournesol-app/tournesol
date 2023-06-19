describe('Settings - preferences page', () => {
  beforeEach(() => {
    cy.recreateUser("test-preferences-page", "test-preferences-page@example.com", "tournesol");
  });

  const login = () => {
    cy.focused().type('test-preferences-page');
    cy.get('input[name="password"]').click().type("tournesol").type('{enter}');
  }

  describe('Navigation', () => {
    it('is accessible from the personal menu', () => {
      cy.visit('/login');
      login();

      cy.get('button#personal-menu-button').click();
      cy.get('#personal-menu').contains('Preferences').click();

      cy.location('pathname').should('equal', '/settings/preferences');
    });
  });

  describe('Setting - display weekly collective goal', () => {
    const fieldSelector = '#videos_comparison_ui__weekly_collective_goal_display';

    it('handles the value ALWAYS', () => {
      cy.visit('/settings/preferences');
      login();

      // Ensure the default value is ALWAYS
      cy.get(
        '[data-testid=videos_weekly_collective_goal_display]'
      ).should('have.value', 'ALWAYS');

      cy.visit('/comparison');
      cy.contains('Weekly collective goal').should('be.visible');
      cy.visit('/comparison?embed=1');
      cy.contains('Weekly collective goal').should('be.visible');
    });

    it('handles the value WEBSITE_ONLY', () => {
      cy.visit('/settings/preferences');
      login();

      cy.get(fieldSelector).click();
      cy.contains('Website only').click();
      cy.contains('Update preferences').click();

      cy.visit('/comparison');
      cy.contains('Weekly collective goal').should('be.visible');
      cy.visit('/comparison?embed=1');
      cy.contains('Weekly collective goal').should('not.exist');

    });

    it('handles the value EMBEDDED_ONLY', () => {
      cy.visit('/settings/preferences');
      login();

      cy.get(fieldSelector).click();
      cy.contains('Extension only').click();
      cy.contains('Update preferences').click();

      cy.visit('/comparison');
      cy.contains('Weekly collective goal').should('not.exist');
      cy.visit('/comparison?embed=1');
      cy.contains('Weekly collective goal').should('be.visible');
    });

    it('handles the value NEVER', () => {
      cy.visit('/settings/preferences');
      login();

      cy.get(fieldSelector).click();
      cy.contains('Never').click();
      cy.contains('Update preferences').click();

      cy.visit('/comparison');
      cy.contains('Weekly collective goal').should('not.exist');
      cy.visit('/comparison?embed=1');
      cy.contains('Weekly collective goal').should('not.exist');
    });
  });

  describe('Setting - criteria order', () => {
    it('handles adding criteria', () => {
      cy.visit('/settings/preferences');
      login();

      cy.contains('No criteria selected.').should('be.visible');

      cy.get('input[id="id_selected_optional_layman_friendly"]').click();
      cy.get('input[id="id_selected_optional_backfire_risk"]').click();
      cy.contains('Update preferences').click();

      cy.visit('/comparison');

      cy.get('div[id="id_container_criteria_layman_friendly"]').next().should('have.text', 'Resilience to backfiring risks ');
      cy.get('div[id="id_container_criteria_reliability"]').should('not.be.visible');

      cy.visit('/settings/preferences');
      cy.wait(1000);
      cy.get('button[aria-label="down_layman_friendly"]').click();
      cy.contains('Update preferences').click();

      cy.visit('/comparison');
      cy.get('div[id="id_container_criteria_backfire_risk"]').next().should('have.text', 'Layman-friendly ');
    });
  });  

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

  describe('Setting - upload date', () => {
    const fieldSelector = '#videos_recommendations__default_date';

    it('handles the value A month ago', () => {
      cy.visit('/settings/preferences');
      login();

      // Ensure the default value is A month ago
      cy.get(
        '[data-testid=videos_recommendations__default_date]'
      ).should('have.value', 'MONTH');

      cy.get('a[aria-label="Link to the recommendations page"]').should(
        'have.attr', 'href', '/recommendations?date=Month'
      );
    });

    it('handles the value A day ago', () => {
      cy.visit('/settings/preferences');
      login();

      cy.get(fieldSelector).click();
      cy.contains('A day ago').click();
      cy.contains('Update preferences').click();

      cy.get('a[aria-label="Link to the recommendations page"]').should(
        'have.attr', 'href', '/recommendations?date=Today&unsafe='
      );
    });

    it('handles the value A week ago', () => {
      cy.visit('/settings/preferences');
      login();

      cy.get(fieldSelector).click();
      cy.contains('A week ago').click();
      cy.contains('Update preferences').click();

      cy.get('a[aria-label="Link to the recommendations page"]').should(
        'have.attr', 'href', '/recommendations?date=Week&unsafe='
      );
    });

    it('handles the value A year ago', () => {
      cy.visit('/settings/preferences');
      login();

      cy.get(fieldSelector).click();
      cy.contains('A year ago').click();
      cy.contains('Update preferences').click();

      cy.get('a[aria-label="Link to the recommendations page"]').should(
        'have.attr', 'href', '/recommendations?date=Year&unsafe='
      );
    });

    it('handles the value All time', () => {
      cy.visit('/settings/preferences');
      login();

      cy.get(fieldSelector).click();
      cy.contains('All time').click();
      cy.contains('Update preferences').click();

      cy.get('a[aria-label="Link to the recommendations page"]').should(
        'have.attr', 'href', '/recommendations?date=&unsafe='
      );
    });
  });

  describe('Setting - unsafe', () => {
    it('handles the value false (hide)', () => {
      cy.visit('/settings/preferences');
      login();

      cy.get('[data-testid=videos_recommendations__default_unsafe]');
      cy.contains('Update preferences').click();

      cy.get('a[aria-label="Link to the recommendations page"]').should(
        'have.attr', 'href', '/recommendations?date=Month&unsafe='
      );
    });

    it('handles the value true (show)', () => {
      cy.visit('/settings/preferences');
      login();

      cy.get('[data-testid=videos_recommendations__default_unsafe]').click();
      cy.contains('Update preferences').click();

      cy.get('a[aria-label="Link to the recommendations page"]').should(
        'have.attr', 'href', '/recommendations?date=Month&unsafe=true'
      );
    });
  });
});
