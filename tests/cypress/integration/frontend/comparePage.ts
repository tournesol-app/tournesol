describe('Comparison page', () => {
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

    describe('video selectors', () => {
        const videoAUrl = 'https://www.youtube.com/watch?v=u83A7DUNMHs';
        const videoBUrl = 'https://www.youtube.com/watch?v=m9APFfDGRuk';

        it('support pasting YouTube URLs', () => {
            cy.visit('/comparison');

            cy.focused().type('user1');
            cy.get('input[name="password"]').click().type('tournesol').type('{enter}');

            cy.contains('video 1', {matchCase: false}).should('be.visible');
            cy.contains('video 2', {matchCase: false}).should('be.visible');

            // TODO: write the test
        })

        it('support pasting YouTube video ID', () => {
            cy.visit('/comparison');

            cy.focused().type('user1');
            cy.get('input[name="password"]').click().type('tournesol').type('{enter}');

            const inputs = cy.get('input[placeholder="Paste URL or Video ID"]');
            inputs.should('have.length', 2);

            inputs.first().type(videoAUrl.split('?v=')[1], {delay: 0});
            inputs.first().get('div[data-testid=video-card-info]').within(() => {
                // the video title is displayed
                cy.contains(
                    'Science4VeryAll : Lê fait enfin un effort de vulgarisation sur Étincelles !!',
                    {matchCase: false}
                ).should('be.visible');
                // the upload date is displayed
                cy.contains('2021-11-22', {matchCase: false}).should('be.visible');
                // the number of view is displayed
                cy.contains('views', {matchCase: false}).should('be.visible');
            });

            cy.get('input[placeholder="Paste URL or Video ID"]')
                .last().type(videoBUrl.split('?v=')[1], {delay: 0});

            cy.get('input[placeholder="Paste URL or Video ID"]')
                .last().get('div[data-testid=video-card-info]').within(() => {
                // the video title is displayed
                cy.contains(
                    'Pourquoi les réseaux sociaux sont si clivants ?',
                    {matchCase: false}
                ).should('be.visible');
                // the upload date is displayed
                cy.contains('2022-02-03', {matchCase: false}).should('be.visible');
                // the number of view is displayed
                cy.contains('views', {matchCase: false}).should('be.visible');
            });
        })
    });
});
