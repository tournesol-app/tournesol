describe('Page - For you', () => {

  const username = "test-feed-foryou-page";

  const login = () => {
    cy.focused().type(username);
    cy.get('input[name="password"]').click().type("tournesol").type('{enter}');
  }

  beforeEach(() => {
    cy.recreateUser(username, `${username}@example.org`, "tournesol");
  });

  describe('Poll - videos', () => {

    describe('General', () => {
      it('requires authentication', () => {
        cy.visit('/feed/foryou');
        cy.location('pathname').should('equal', '/login');
        login();
        cy.location('pathname').should('equal', '/feed/foryou');
      });

      it('is accessible from the side bar', () => {
        cy.visit('/login');
        login();

        cy.contains('For you').click();
        cy.location('pathname').should('equal', '/feed/foryou');
      });
    });

    describe('Pagination', () => {
      it("doesn't display pagination when there is no items", () => {
        cy.visit('/feed/foryou');
        login();
        cy.contains('button', '< -10', {matchCase: false}).should('not.exist');
        cy.contains('button', '< -1', {matchCase: false}).should('not.exist');
        cy.contains('button', '+1 >', {matchCase: false}).should('not.exist');
        cy.contains('button', '+10 >', {matchCase: false}).should('not.exist');

        cy.contains(
          "There doesn't seem to be anything to display at the moment.",
          {matchCase: false}
        ).should('be.visible');
      });
    });

    describe('Action bar', () => {
      it('displays links to Search and Preferences', () => {
        cy.visit('/feed/foryou');
        login();

        cy.get('a[data-testid="icon-link-to-search-page"]').click();
        cy.location('pathname').should('equal', '/search');

        cy.get('a[data-testid="icon-link-back-to-previous-page"]').click();

        cy.location('pathname').should('equal', '/feed/foryou');
        cy.get('a[data-testid="icon-link-to-preferences-page"]').click();
        cy.location('pathname').should('equal', '/settings/preferences');
      });
    });

    describe('Search filters', () => {
      it("doesn't display seach filters", () => {
        cy.visit('/feed/foryou');
        login();
        cy.contains('Filters', {matchCase: true}).should('not.exist');
        cy.location('search').should('equal', '');
      });
    });
  });
});
