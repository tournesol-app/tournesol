describe('Rate-later page', () => {
  before(() => {
    cy.sql("TRUNCATE tournesol_videoratelater");
  })

  it('can add video to rate-later list', () => {
    cy.visit('/rate_later');
    cy.location('pathname').should('equal', '/login');
    cy.focused().type('user');
    cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
    cy.contains('0 video').should('be.visible');
    cy.get('input[placeholder="Video id or URL"]').type('dQw4w9WgXcQ').type('{enter}');
    cy.contains('1 video').should('be.visible');
  })
})
