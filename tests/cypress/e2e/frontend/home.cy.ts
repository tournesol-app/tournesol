describe('Home', () => {
  describe('Poll - videos', () => {

    describe('anonymous users', () => {
      it('contains recommended videos', () => {
        cy.visit('/');
        cy.contains('See more videos').should('be.visible');
        cy.contains('See more videos').click();
        cy.location('pathname').should('equal', '/search');
      });
    });

    describe('authenticated users', () => {
      it('doesnt contain a link to signup', () => {
        cy.visit('/');
        cy.contains('Create account').should('not.exist');
      });

      it('contains a link to the comparison page', () => {
        cy.visit('/');
        cy.contains('Compare the videos').click();

        cy.focused().type('aidjango');
        cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
        cy.location('pathname').should('equal', '/comparison');
      });
    });
  });
});
