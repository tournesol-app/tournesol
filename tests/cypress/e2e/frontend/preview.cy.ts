describe('Preview of recommenations via API', () => {

  it('page search with filters', () => {
    cy.visit('/search');
    cy.contains('Filters', { matchCase: false }).click();
    cy.contains('A week ago', { matchCase: false }).click();
    cy.url().then(url => {
      const previewUrl = url.replace("http://localhost:3000/", "http://localhost:8000/preview/");
      cy.request({
        url: previewUrl,
        followRedirect: false,
      },).then(
        response => {
          expect(response.status).to.equal(302);
          const redirectLocation = response.headers.location;
          expect(redirectLocation).to.contain("date_gte=")
          expect(redirectLocation).to.not.contain("metadata%5Blanguage%5D=")
        }
      );
    });
  });

  it('page feed/top with filters', () => {
    cy.visit('/feed/top?language=fr');
    cy.contains('Filters', { matchCase: false }).click();
    cy.url().then(url => {
      const previewUrl = url.replace("http://localhost:3000/", "http://localhost:8000/preview/");
      cy.request({
        url: previewUrl,
        followRedirect: false,
      },).then(
        response => {
          expect(response.status).to.equal(302);
          const redirectLocation = response.headers.location;
          expect(redirectLocation).to.not.contain("date_gte=")
          expect(redirectLocation).to.contain("metadata%5Blanguage%5D=fr")
        }
      );
    });
  });


  it('(legacy) page recommendations with filters', () => {
    cy.visit('/recommendations?language=en');
    cy.contains('Filters', { matchCase: false }).click();
    cy.contains('A week ago', { matchCase: false }).click();
    cy.url().then(url => {
      const previewUrl = url.replace("http://localhost:3000/", "http://localhost:8000/preview/");
      cy.request({
        url: previewUrl,
        followRedirect: false,
      },).then(
        response => {
          expect(response.status).to.equal(302);
          const redirectLocation = response.headers.location;
          expect(redirectLocation).to.contain("date_gte=")
          expect(redirectLocation).to.contain("metadata%5Blanguage%5D=en")
        }
      );
    });
  });
})
