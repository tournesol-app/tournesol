describe('Home', () => {
  describe('Poll - videos', () => {

    describe('anonymous users', () => {
      it('contains a link to signup', () => {
        cy.visit('/');
        cy.contains('Create account').should('be.visible');
        cy.contains('Create account').click()
        cy.location('pathname').should('equal', '/signup');
      });

      it('contains a link to the tutorial', () => {
        cy.visit('/');
        
        cy.contains('Start').should('be.visible');
        cy.contains('Create account').should('be.visible');
  
        cy.contains('Start').click()
        cy.location('pathname').should('equal', '/login');
      });
    });

    describe('authenticated users', () => {
      before(() => {
        cy.recreateUser("new-user-no-comp", "new-user-no-comp@domain.test", "tournesol");
      })

      it('doesnt contain a link to signup', () => {
        cy.visit('/');
        cy.contains('Create account').should('not.exist');
      });

      it('contains a link to the tutorial', () => {
        cy.visit('/');
        cy.contains('Start').click()
  
        cy.focused().type('aidjango');
        cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
        
        // Users having already several comparisons are considered as having
        // already finished the tutorial, and should be redirected to the
        // comparison page without the parameter ?series=true.
        cy.location('pathname').should('equal', '/comparison');
        cy.location('search').should('equal', '');
      });

      it('contains a link to the tutorial - new user', () => {
        cy.visit('/');
        cy.contains('Start').click()
  
        cy.focused().type('new-user-no-comp');
        cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
  
        cy.location('pathname').should('equal', '/comparison');
        cy.location('search').should('equal', '?series=true');
      });
    });
  });
});
