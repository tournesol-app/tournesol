describe('Page Not Found', () => {
  it('displays 404 page for non-existing routes and allows navigation back to home', () => {
    cy.visit('/this-page-does-not-exist-12345');
    cy.contains('Sorry, page not found.').should('be.visible');
    cy.contains('Back to home page').should('be.visible');
    cy.contains('Back to home page').click();
    cy.location('pathname').should('equal', '/');
  });
});

