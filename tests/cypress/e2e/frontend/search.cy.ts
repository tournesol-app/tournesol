describe('Search', () => {
  describe('with a YouTube URL', () => {
    it('redirect automatically to the analysis page', () => {
      const videoURL = 'https://www.youtube.com/watch?v=b6vdKFxCvfU';
      const videoId = 'b6vdKFxCvfU';

      // Intercept the request to the API
      cy.intercept('GET', `/polls/videos/entities/yt:${videoId}/**`).as('videopoll');

      cy.visit('/');
      cy.get('input[id="searchInput"]').click().type(`${videoURL}{enter}`);


      cy.url().should('include', `/entities/yt:${videoId}`)
      cy.wait(`@videopoll`).its('response.statusCode').should('eq', 200);
    });
  });

  describe('with a Tournesol video UID', () => {
    it('redirect automatically to the analysis page', () => {
      const videoId = 'WPPPFqsECz0';

      // Intercept the request to the API
      cy.intercept('GET', `/polls/videos/entities/yt:${videoId}/**`).as('videopoll');

      cy.visit('/');
      cy.get('input[id="searchInput"]').click().type(`yt:${videoId}{enter}`);

      cy.wait(`@videopoll`).its('response.statusCode').should('eq', 200);
    });
  });
});
