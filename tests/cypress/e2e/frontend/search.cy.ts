describe('Search', () => {
    describe('YouTube URL search', () => {
        it('redirects automatically to the corresponding video page', () => {
            const videoURL = 'https://www.youtube.com/watch?v=b6vdKFxCvfU';
            const videoUID = 'b6vdKFxCvfU';

            // Intercept the AJAX request to API for specific video
            cy.intercept('GET', `/polls/videos/entities/yt:${videoUID}/**`).as('videopoll')

            // Visit main page (should work on every page since search bar is the same)
            cy.visit('/');

            // Input the video URL
            cy.get('input[id="searchInput"]').click().type(`${videoURL}{enter}`);
            
            // Redirection to video page
            cy.url().should('include', `/entities/yt:${videoUID}`)

            // Check if AJAX returns 200
            cy.wait(`@videopoll`).its('response.statusCode').should('eq', 200)
        })
    });

    describe('YouTube video UID search', () => {
        it('redirects automatically to the corresponding video page', () => {
            // https://youtu.be/WPPPFqsECz0
            const videoUID = 'WPPPFqsECz0';

            // Intercept the AJAX request to API for specific video
            cy.intercept('GET', `/polls/videos/entities/yt:${videoUID}/**`).as('videopoll')

            // Visit main page (should work on every page since search bar is the same)
            cy.visit('/');

            // Input the video URL
            cy.get('input[id="searchInput"]').click().type(`yt:${videoUID}{enter}`);

            // Check if AJAX returns 200
            cy.wait(`@videopoll`).its('response.statusCode').should('eq', 200)
        });
    });
});