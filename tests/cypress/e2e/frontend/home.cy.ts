describe('Home', () => {
  describe('Poll - videos', () => {

    describe('anonymous users', () => {
      it('contains a link to signup', () => {
        cy.visit('/');
        cy.contains('Create account').should('be.visible');
        cy.contains('Create account').click();
        cy.location('pathname').should('equal', '/signup');
      });

      it('contains a link to the tutorial', () => {
        cy.visit('/');

        cy.contains('Start').should('be.visible');
        cy.contains('Create account').should('be.visible');

        cy.contains('Start').click();
        cy.location('pathname').should('equal', '/login');
      });
    });

    describe('authenticated users', () => {
      it('doesnt contain a link to signup', () => {
        cy.visit('/');
        cy.contains('Create account').should('not.exist');
      });

      it('contains a link to the comparison page', () => {
        cy.visit('/');
        cy.contains('Start').click();

        cy.focused().type('aidjango');
        cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
        cy.location('pathname').should('equal', '/comparison');
      });
    });
  });
});
