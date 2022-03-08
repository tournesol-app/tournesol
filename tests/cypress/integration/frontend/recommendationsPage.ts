describe('Recommendations', () => {
    it('sets default languages properly and backward navigation works', () => {
      cy.visit('/');
      cy.location('pathname').should('equal', '/');
      cy.contains('Recommendations').click();
      cy.location('search').should('contain', 'language=en')
      cy.go('back')
      cy.location('pathname').should('equal', '/');
    })
  })
