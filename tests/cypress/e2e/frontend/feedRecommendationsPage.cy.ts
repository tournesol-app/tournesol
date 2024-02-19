describe('Feed - collective recommendations', () => {
  const username = "test-feed-reco-page";

  beforeEach(() => {
    cy.recreateUser(username, "test-feed-reco-page@example.com", "tournesol");
  });

  const login = () => {
    cy.focused().type(username);
    cy.get('input[name="password"]').click().type("tournesol").type('{enter}');
  }

  describe('redirection', () => {
    it('anonymous users are redirected with default filters', () => {
      cy.visit('/feed/recommendations');
      cy.location('pathname').should('equal', '/recommendations');
      cy.location('search').should('contain', '?date=Month');
    });

    it('authenticated users are redirected with their preferences', () => {
      cy.visit('/settings/preferences');
      login();

      cy.get('#videos_recommendations__default_date').click();
      cy.contains('A day ago').click();
      cy.get('[data-testid=videos_recommendations__default_unsafe]').click();
      cy.get('[data-testid=videos_recommendations__default_exclude_compared_entities]').click();
      cy.contains('Update preferences').click();

      cy.visit('/feed/recommendations');
      cy.location('pathname').should('equal', '/recommendations');
      cy.location('search')
        .should('contain', '?date=Today&advanced=unsafe%2Cexclude_compared&language=en');
    });
  });
});
