describe('Preview of Recommendations page via API', () => {
  it('supports a preview of a recommendations page with filters', () => {
    cy.visit('/recommendations');
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
      )
    });
  })
})
