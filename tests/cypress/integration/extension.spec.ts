import { skipOn, onlyOn } from '@cypress/skip-test'

onlyOn('headed', () => {
  describe('Tournesol extension', 
    { browser: ['chromium', 'chrome']}, 
    () => {
      it('shows Tournesol recommendations on youtube.com', () => {
        cy.on('uncaught:exception', (err, runnable) => {
          // returning false here prevents Cypress from
          // failing the test, because of unrelated Youtube errors
          return false
        })

        cy.visit('https://www.youtube.com');
        cy.wait(5000);
        cy.contains('Recommended by Tournesol').should('be.visible');
      })
    })
})