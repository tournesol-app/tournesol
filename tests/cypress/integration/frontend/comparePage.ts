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

    it('support pasting YouTube URLs', () => {
      cy.visit('/comparison');

      cy.focused().type('user1');
      cy.get('input[name="password"]').click()
        .type('tournesol').type('{enter}');

      cy.contains('video 1', {matchCase: false}).should('be.visible');
      cy.contains('video 2', {matchCase: false}).should('be.visible');

      // TODO: a little help is required to write the tests

      // I didn't find a proper way to paste the URL into the `VideoCard` input field,
      // and to trigger its `onChange` method to extract the video ID from the URL.
      // .type() didn't work
      // .invoke('val', url) didn't work neither
      // .invoke('val', url).trigger('change') / trigger('input') neither
    })

    it('support pasting YouTube video ID', () => {
      cy.visit('/comparison');

      cy.focused().type('user1');
      cy.get('input[name="password"]').click()
        .type('tournesol').type('{enter}');

      // two cards must be displayed
      cy.get('input[placeholder="Paste URL or Video ID"]')
        .should('have.length', 2);

      cy.get('input[placeholder="Paste URL or Video ID"]').first()
        .type(videoAUrl.split('?v=')[1], {delay: 0});

      // the video title, upload date, and the number of views must be displayed
      cy.get('div[data-testid=video-card-info]').first().within(() => {
        cy.contains(
          'Science4VeryAll : Lê fait enfin un effort de vulgarisation sur Étincelles !!',
          {matchCase: false}
        ).should('be.visible');
        cy.contains('2021-11-22', {matchCase: false}).should('be.visible');
        cy.contains('views', {matchCase: false}).should('be.visible');
      });
    })
  });

  describe('submit a comparison', () => {
    const videoAUrl = 'https://www.youtube.com/watch?v=u83A7DUNMHs';
    const videoBUrl = 'https://www.youtube.com/watch?v=6jK9bFWE--g';

    it('with only the main criteria', () => {
      cy.visit('/comparison');

      cy.focused().type('user1');
      cy.get('input[name="password"]').click()
        .type('tournesol').type('{enter}');

      cy.get('input[placeholder="Paste URL or Video ID"]').first()
        .type(videoAUrl.split('?v=')[1], {delay: 0});

      // TODO: click on the New Video button instead to guarantee
      //       the comparison doesn't already exist
      cy.get('input[placeholder="Paste URL or Video ID"]').last()
        .type(videoBUrl.split('?v=')[1], {delay: 0});

      cy.contains('should be largely recommended', {matchCase: false})
        .should('be.visible');

      cy.contains('submit', {matchCase: false})
        .should('be.visible');

      cy.get('button#expert_submit_btn').click();

      cy.contains('edit comparison', {matchCase: false})
        .should('be.visible');
    })
  });
});
