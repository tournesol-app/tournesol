import { curry } from "cypress/types/lodash";

describe('Public personal recommendations page', () => {

  describe('Poll - videos', () => {
    describe('for anonymous users', () => {
      it('displays public personal reco. of users, by URL', () => {
        cy.visit('/users/user/recommendations');
        cy.contains('Personal recommendations');
        cy.contains('by user');
      });
    });
  
    describe('for authenticated users', () => {
      it('displays public personal reco. of users, by URL', () => {
        cy.visit('/');
        cy.contains('Log in').click();
        cy.focused().type('user');
        cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
  
        cy.visit('/users/user/recommendations');
        cy.contains('Personal recommendations');
        cy.contains('by user');
      });
  
      it('displays public personal reco. of users, by personal menu', () => {
        cy.visit('/');
        cy.contains('Log in').click();
        cy.focused().type('user');
        cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
    
        cy.get('button#personal-menu-button').click();
        cy.contains('My recommendations').should('be.visible');
  
        cy.contains('My recommendations').click();
        cy.location('pathname').should('equal', '/users/user/recommendations');
        // The menu must lead to the all-time recommendations.
        cy.location('search').should('contain', 'date=');
        cy.contains('Personal recommendations');
        cy.contains('by user');
      });
    });
  });

  describe('Poll - presidentielle2022', () => {
    describe('for anonymous users', () => {
      it('displays 404 instead of public personal reco.', () => {
        cy.visit('/presidentielle2022/users/user/recommendations');
        cy.contains('Sorry, page not found');
      });
    });
  
    describe('for authenticated users', () => {
      it('displays 404 instead of public personal reco.', () => {
        cy.visit('/presidentielle2022');
        cy.contains('Log in').click();
        cy.focused().type('user');
        cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
  
        cy.visit('/presidentielle2022/users/user/recommendations');
        cy.contains('Sorry, page not found');
      });

      it("doesn't the public personal reco. link in the personal menu", () => {
        cy.visit('/presidentielle2022');
        cy.contains('Log in').click();
        cy.focused().type('user');
        cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
  
        
        cy.get('button#personal-menu-button').click();
        cy.contains('My recommendations').should('not.exist');
      });
    });
  });
});
