describe('Page - For you', () => {
  const login = () => {
    cy.focused().type('user');
    cy.get('input[name="password"]').click().type("tournesol").type('{enter}');
  }

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

    /*
    describe('Pagination', () => {
      it('displays the pagination', () => {
        cy.visit('/feed/foryou');
        cy.contains('button', '< -10', {matchCase: false}).should('exist');
        cy.contains('button', '< -1', {matchCase: false}).should('exist');
        cy.contains('button', '+1 >', {matchCase: false}).should('exist');
        cy.contains('button', '+10 >', {matchCase: false}).should('exist');
      });
    });
    */

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
