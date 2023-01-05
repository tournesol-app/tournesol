describe('Comparison page', () => {

  const deleteComparison = (username, idA, idB) => {
    cy.sql(`
        DELETE FROM tournesol_comparisoncriteriascore
        WHERE comparison_id = (
            SELECT id
            FROM tournesol_comparison
            WHERE entity_1_id = (
                SELECT id FROM tournesol_entity WHERE metadata->>'video_id' = '${idA}'
            ) AND entity_2_id = (
                SELECT id FROM tournesol_entity WHERE metadata->>'video_id' = '${idB}'
            ) AND user_id = (
                SELECT id FROM core_user WHERE username = '${username}'
            )
        );
      `);

    cy.sql(`
        DELETE FROM tournesol_comparison
            WHERE entity_1_id = (
                SELECT id FROM tournesol_entity WHERE metadata->>'video_id' = '${idA}'
            ) AND entity_2_id = (
                SELECT id FROM tournesol_entity WHERE metadata->>'video_id' = '${idB}'
            ) AND user_id = (
                SELECT id FROM core_user WHERE username = '${username}'
            );
      `);
  };

  const waitForAutoFill = () => {
    cy.get('div[data-testid=video-card-info]')
      .should('have.length', 2);
  }

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

      cy.contains('video 1', {matchCase: false}).should('be.visible');
      cy.contains('video 2', {matchCase: false}).should('be.visible');
    })
  });

  describe('video selectors', () => {
    const videoAUrl = 'https://www.youtube.com/watch?v=u83A7DUNMHs';

    it('support pasting YouTube URLs', () => {
      cy.visit('/comparison');

      cy.focused().type('user1');
      cy.get('input[name="password"]').click()
        .type('tournesol').type('{enter}');

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

      waitForAutoFill();

      cy.get('input[placeholder="Paste URL or Video ID"]').first()
        .type(videoAUrl.split('?v=')[1], {delay: 0});

      // wait for the auto filled video to be replaced
      cy.contains('Science4VeryAll');

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
    const username = 'user1';
    const videoAId = 'u83A7DUNMHs';
    const videoBId = '6jK9bFWE--g';

    const optionalCriteriaSliders = [
      "slider_expert_reliability",
      "slider_expert_pedagogy",
      "slider_expert_importance",
      "slider_expert_layman_friendly",
      "slider_expert_entertaining_relaxing",
      "slider_expert_engaging",
      "slider_expert_diversity_inclusion",
      "slider_expert_better_habits",
      "slider_expert_backfire_risk",
    ];

    beforeEach(() => {
      deleteComparison(username, videoAId, videoBId);
    })

    after(() => {
      deleteComparison(username, videoAId, videoBId);
    })

    /**
     * A user can submit a comparison with only the main criteria.
     *
     * The test ensures:
     * - only the main criteria is visible
     * - the add optional criteria button is displayed
     * - success hints are visible (edit button and success alert)
     */
    it('works with only the main criteria', () => {
      cy.visit('/comparison');

      cy.focused().type(username);
      cy.get('input[name="password"]').click()
        .type('tournesol').type('{enter}');

      waitForAutoFill();

      // add one video, and ask for a second one
      cy.get('input[placeholder="Paste URL or Video ID"]').first()
        .type(videoAId, {delay: 0});
      cy.get('input[placeholder="Paste URL or Video ID"]').last()
        .type(videoBId, {delay: 0});

      // only one criteria must be visible by default
      cy.contains('add optional criteria', {matchCase: false})
        .scrollIntoView()
        .should('be.visible');
      cy.contains('should be largely recommended', {matchCase: false})
        .should('be.visible');

      cy.get('#slider_expert_largely_recommended').within(() => {
        cy.get('span[data-index=12]').click();
      })

      cy.contains('submit', {matchCase: false})
        .should('be.visible');
      cy.get('button#expert_submit_btn').click();

      cy.contains('edit comparison', {matchCase: false})
        .should('be.visible');
      cy.contains('successfully submitted', {matchCase: false})
        .should('be.visible');
    });

    it('works with all the criteria', () => {
      cy.visit('/comparison');

      cy.focused().type(username);
      cy.get('input[name="password"]').click()
        .type('tournesol').type('{enter}');

      waitForAutoFill();

      cy.get('input[placeholder="Paste URL or Video ID"]').first()
        .type(videoAId, {delay: 0});
      cy.get('input[placeholder="Paste URL or Video ID"]').last()
        .type(videoBId, {delay: 0});

      cy.contains('add optional criteria', {matchCase: false}).click()

      cy.get('#slider_expert_largely_recommended').within(() => {
        cy.get('span[data-index=12]').click();
      })

      optionalCriteriaSliders.forEach((slider) => {
        cy.get('#' + slider).within(() => {
          cy.get('span[data-index=12]').click();
        })
      });

      cy.contains('submit', {matchCase: false})
        .should('be.visible');
      cy.get('button#expert_submit_btn').click();

      cy.contains('edit comparison', {matchCase: false})
        .should('be.visible');
      cy.contains('successfully submitted', {matchCase: false})
        .should('be.visible');
    });

    it('doesn\'t allow comparing a video with itself', () => {
      cy.visit('/comparison');

      cy.focused().type(username);
      cy.get('input[name="password"]').click()
          .type('tournesol').type('{enter}');

      waitForAutoFill();

      cy.get('input[placeholder="Paste URL or Video ID"]').first()
          .type(videoAId, {delay: 0});
      cy.get('input[placeholder="Paste URL or Video ID"]').last()
          .type(videoAId, {delay: 0});

      cy.contains('These two items are very similar', {matchCase: false})
          .should('be.visible');

      cy.contains('add optional criteria', {matchCase: false})
          .should('not.exist');
      cy.contains('should be largely recommended', {matchCase: false})
          .should('not.exist');
      cy.get('button#expert_submit_btn').should('not.exist');
    });
  });

  describe('access a comparison page', () => {
    it('redirects legacy video params to corresponding uids', () => {
      const videoAId = 'u83A7DUNMHs';
      const videoBId = '6jK9bFWE--g';

      cy.visit(`/comparison/?videoA=${videoAId}&videoB=${videoBId}`);
      cy.focused().type('user1');
      cy.get('input[name="password"]').click().type('tournesol').type('{enter}');

      cy.location('search').should('contain', `uidA=yt%3A${videoAId}`)
      cy.location('search').should('contain', `uidB=yt%3A${videoBId}`)

      cy.get('input[placeholder="Paste URL or Video ID"]').first()
        .should('have.value', `yt:${videoAId}`);
      cy.get('input[placeholder="Paste URL or Video ID"]').last()
        .should('have.value', `yt:${videoBId}`);
    });
  })
});
