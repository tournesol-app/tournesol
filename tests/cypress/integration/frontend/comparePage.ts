describe('Compare page', () => {
    describe('authorization', () => {
        it('is not accessible by anonymous users', () => {
            cy.visit('/comparison');
            cy.location('pathname').should('equal', '/login');
            cy.contains('log in to tournesol', {matchCase: false}).should('be.visible');
        })

        it('is accessible by authenticated users', () => {
            cy.visit('/comparison');

            cy.focused().type('user1');
            cy.get('input[name="password"]').click().type('tournesol').type('{enter}');

            cy.location('pathname').should('equal', '/comparison');
            cy.contains('submit a comparison', {matchCase: false}).should('be.visible');
        })
    });
});
