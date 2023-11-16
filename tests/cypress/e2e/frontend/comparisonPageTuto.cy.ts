describe('Comparison page tutorial', () => {
  const username = "test-comparison-tutorial";

  before(() => {
    cy.recreateUser(username, 'test-comparison-tutorial@example.com', 'tournesol');
  });

  describe('initial state', () => {
    it('collective goal is not displayed', () => {
      cy.visit('/comparison');
      cy.focused().type(username);
      cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
      cy.contains('Weekly collective goal').should('not.exist');
    });
  });

  describe('tutorial behavior', () => {
    it('follows the course of the tutorial', () => {
      cy.visit('/comparison');
      cy.focused().type(username);
      cy.get('input[name="password"]').click().type('tournesol').type('{enter}');

      cy.get('[data-testid=tip-id-0]').should('be.visible');
      // The navigation between tips is not possible yet.
      cy.get('[data-testid=tips-prev]').should('have.attr', 'disabled');
      cy.get('[data-testid=tips-next]').should('have.attr', 'disabled');


      cy.get('button#expert_submit_btn').click();

      cy.get('[data-testid=tip-id-1]').should('be.visible');
      // After one comparison it's possible to display the previous tips.
      cy.get('[data-testid=tips-prev]').should('not.have.attr', 'disabled');
      cy.get('[data-testid=tips-next]').should('have.attr', 'disabled');


      cy.get('button#expert_submit_btn').click();

      cy.get('[data-testid=tip-id-2]').should('be.visible');
      cy.get('[data-testid=tips-prev]').should('not.have.attr', 'disabled');
      cy.get('[data-testid=tips-next]').should('have.attr', 'disabled');

      cy.get('button#expert_submit_btn').click();

      // After 3 comparisons, the user is invited to install the extension.
      cy.contains("Install the extension");
      cy.contains("button", "continue").click();

      cy.get('[data-testid=tip-id-3]').should('be.visible');

      for (var tutorialLength = 0; tutorialLength < 3; tutorialLength++) {
        cy.get('[data-testid=tips-prev]').should('not.have.attr', 'disabled');
        cy.get('[data-testid=tips-prev]').click();
      }

      cy.get('[data-testid=tips-prev]').should('have.attr', 'disabled');

      for (var tutorialLength = 0; tutorialLength < 3; tutorialLength++){
        cy.get('[data-testid=tips-next]').should('not.have.attr', 'disabled');
        // A snackbar may hide the tips-next button and persist for 5 seconds.
        cy.get('[data-testid=tips-next]').click({timeout: 6000});
      }

      cy.get('[data-testid=tips-next]').should('have.attr', 'disabled');

      cy.get('button#expert_submit_btn').click();
      cy.contains('Weekly collective goal').should('be.visible');
    });
  });
});
