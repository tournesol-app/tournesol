describe('Comparison page tutorial', () => {
  const username = "test-comparison-tutorial";

  before(() => {
    cy.recreateUser(username, "test-comparison-tutorial@example.com", "tournesol");
  });

  describe('collective goal', () => {
    it('is not displayed during tutorial', () => {
      cy.visit('/comparison');
      cy.focused().type(username);
      cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
      cy.contains('Weekly collective goal').should('not.exist');
    })
  });

  describe('tutorial behavior', () => {
    it('follows the course of the tutorial', () => {
      cy.visit('/comparison');
      cy.focused().type(username);
      cy.get('input[name="password"]').click().type('tournesol').type('{enter}');

      cy.get('[data-testid=tip_prev]').should('have.attr', 'tabindex', '-1');
      cy.get('[data-testid=tip_next]').should('have.attr', 'tabindex', '-1');
      cy.get('button#expert_submit_btn').click();

      cy.get('[data-testid=tip_prev]').should('have.attr', 'tabindex', '0');
      cy.get('[data-testid=tip_next]').should('have.attr', 'tabindex', '-1');
      cy.get('button#expert_submit_btn').click();

      cy.get('[data-testid=tip_prev]').should('have.attr', 'tabindex', '0');
      cy.get('[data-testid=tip_next]').should('have.attr', 'tabindex', '-1');
      cy.get('button#expert_submit_btn').click();

      cy.contains("Install the extension");
      cy.contains("button", "continue").click();
      for (var tutorialLength=0; tutorialLength<3; tutorialLength++){
        cy.get('[data-testid=tip_prev]').should('have.attr', 'tabindex', '0').click();
      }
      cy.get('[data-testid=tip_prev]').should('have.attr', 'tabindex', '-1');
      for (var tutorialLength=0; tutorialLength<3; tutorialLength++){
        cy.get('[data-testid=tip_next]').should('have.attr', 'tabindex', '0').click();
      }
      cy.get('[data-testid=tip_next]').should('have.attr', 'tabindex', '-1');
      cy.get('button#expert_submit_btn').click();

      cy.contains('Weekly collective goal').should('be.visible');
    })
  });

});
  