describe('Home page comparison feature - anonymous', () => {
  it('doesn\'t display the comparison UI for anonymous users', () => {
    cy.visit('/');
    cy.contains('give your opinion now', {matchCase: false}).should('not.exist');
  });
});

describe('Home page comparison feature - logged', () => {
  it('displays the comparison UI for logged users', () => {
    cy.visit('/login')
    cy.focused().type('user');
    cy.get('input[name="password"]').click().type('tournesol').type('{enter}');

    cy.contains('give your opinion now', {matchCase: false}).should('be.visible');
    cy.contains('should be largely recommended', {matchCase: false}).should('be.visible');

    cy.get('#expert_submit_btn').click();
    cy.get('#expert_submit_btn').contains('edit comparison', {matchCase: false});
  });
});
