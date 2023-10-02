describe('Comparison page', () => {
  const username = "test-comparison-page";
  const ids1 = ["yt:hdAEGAwlK0M", "yt:lYXQvHhfKuM"];
  const ids2 = ["yt:sGLiSLAlwrY", "yt:or5WdufFrmI"];

  /**
   * Create as much comparisons as required to not trigger the tutorial.
   */
  const createComparisons = () => {
    ids1.forEach(uid1 => {
      ids2.forEach(uid2 => {

        cy.sql(`
          WITH ent AS (
            SELECT
              (SELECT id FROM tournesol_entity WHERE uid = '${uid1}') AS uid1,
              (SELECT id FROM tournesol_entity WHERE uid = '${uid2}') AS uid2
          )
          INSERT INTO tournesol_comparison (
            user_id,
            entity_1_id,
            entity_2_id,
            entity_1_2_ids_sorted,
            poll_id
          ) VALUES (
            (SELECT id FROM core_user WHERE username = '${username}'),
            (SELECT uid1 FROM ent),
            (SELECT uid2 FROM ent),
            (SELECT uid1 FROM ent) || '__' || (SELECT uid2 FROM ent),
          1);
        `);
      });
    });
  };

  const deleteComparison = (idA, idB) => {
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

  const deleteComparisons = () => {
    cy.sql(`
      DELETE FROM tournesol_comparisoncriteriascore
      WHERE comparison_id IN (
          SELECT id
          FROM tournesol_comparison
          WHERE user_id = (
              SELECT id FROM core_user WHERE username = '${username}'
          )
      );
    `);

    cy.sql(`
      DELETE FROM tournesol_comparison
          WHERE user_id = (
              SELECT id FROM core_user WHERE username = '${username}'
          );
    `);
  };

  before(() => { // create 4 comparisons to avoid being in the tutorial context
    cy.recreateUser(username, "test-comparison-page@example.com", "tournesol");
    createComparisons();
  });

  after(() => {
    deleteComparisons();
  });

  const waitForAutoFill = () => {
    cy.get('div[data-testid=video-card-info]')
      .should('have.length', 2);
  }

  const pasteInVideoInput = (value: string) => {
    cy.get("[data-testid=paste-video-url] input")
      .focus()
      .invoke("val", value)
      // For some reason typing an additional character is needed for all event handlers
      // to get the change. But a whitespace would be trimmed and ignored by the EntitySelector,
      // so we put an arbitrary character and delete it right away.
      .type("_{backspace}", {delay: 0});
  }

  describe('authorization', () => {
    it('is not accessible by anonymous users', () => {
      cy.visit('/comparison');
      cy.location('pathname').should('equal', '/login');
      cy.contains('log in to tournesol', {matchCase: false}).should('be.visible');
    });

    it('is accessible by authenticated users', () => {
      cy.visit('/comparison');

      cy.focused().type(username);
      cy.get('input[name="password"]').click().type('tournesol').type('{enter}');

      cy.location('pathname').should('equal', '/comparison');
      cy.contains('submit a comparison', {matchCase: false}).should('be.visible');

      cy.contains('A', {matchCase: true});
      cy.contains('B', {matchCase: true});
    });
  });

  it("doesn't break the browser's back button", () => {
    cy.visit('/comparison');
    cy.focused().type(username);
    cy.get('input[name="password"]').click().type('tournesol').type('{enter}');

    cy.get("[data-testid=entity-select-button-compact]").should('have.length', 2);
    cy.get("[data-testid=entity-select-button-compact]").first().click();

    cy.visit('/');
    cy.location('pathname').should('equal', '/');
    cy.contains('Compare').click();
    waitForAutoFill();
    cy.go('back');
    cy.location('pathname').should('equal', '/');
  });

  describe('video selectors', () => {
    const videoAId = "lYXQvHhfKuM";
    const videoAUrl = `https://www.youtube.com/watch?v=${videoAId}`;

    it('support pasting YouTube URLs', () => {
      cy.visit('/comparison');

      cy.focused().type(username);
      cy.get('input[name="password"]').click()
        .type('tournesol').type('{enter}');

      waitForAutoFill();

      cy.get("[data-testid=entity-select-button-compact]").first().click();
      pasteInVideoInput(videoAUrl);

      // wait for the auto filled video to be replaced
      cy.contains('5 IA surpuissantes');

      // the video title, upload date, and the number of views must be displayed
      cy.get('div[data-testid=video-card-info]').first().within(() => {
        cy.contains(
          '5 IA surpuissantes',
          {matchCase: false}
        ).should('be.visible');
        cy.contains('2022-06-20', {matchCase: false}).should('be.visible');
        cy.contains('views', {matchCase: false}).should('be.visible');
      });

      cy.get("[data-testid=entity-select-button-compact]").first().click();
      cy.get("[data-testid=paste-video-url] input[type=text]")
        .should('have.attr', 'value', `yt:${videoAId}`);
    });

    it('support pasting YouTube video ID', () => {
      cy.visit('/comparison');

      cy.focused().type(username);
      cy.get('input[name="password"]').click()
        .type('tournesol').type('{enter}');

      // two cards must be displayed
      cy.get("[data-testid=entity-select-button-compact]").should('have.length', 2);

      waitForAutoFill();

      cy.get("[data-testid=entity-select-button-compact]").first().click();
      pasteInVideoInput(videoAId);

      // wait for the auto filled video to be replaced
      cy.contains('5 IA surpuissantes');

      // the video title, upload date, and the number of views must be displayed
      cy.get('div[data-testid=video-card-info]').first().within(() => {
        cy.contains(
          '5 IA surpuissantes',
          {matchCase: false}
        ).should('be.visible');
        cy.contains('2022-06-20', {matchCase: false}).should('be.visible');
        cy.contains('views', {matchCase: false}).should('be.visible');
      });

      cy.get("[data-testid=entity-select-button-compact]").first().click();
      cy.get("[data-testid=paste-video-url] input[type=text]")
        .should('have.attr', 'value', `yt:${videoAId}`);
    });
  });

  describe('submit a comparison', () => {
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
      deleteComparison(videoAId, videoBId);
    });

    after(() => {
      deleteComparison(videoAId, videoBId);
    });

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
      cy.get("[data-testid=entity-select-button-compact]").first().click();
      pasteInVideoInput(videoAId);

      cy.get("[data-testid=entity-select-button-compact]").last().click();
      pasteInVideoInput(videoBId);

      // only one criteria must be visible by default
      cy.contains('add optional criteria', {matchCase: false})
        .scrollIntoView()
        .should('be.visible');
      cy.contains('should be largely recommended', {matchCase: false})
        .should('be.visible');

      cy.get('#slider_expert_largely_recommended').within(() => {
        cy.get('span[data-index=12]').click();
      });

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

      cy.get("[data-testid=entity-select-button-compact]").first().click();
      pasteInVideoInput(videoAId);
      cy.get("[data-testid=entity-select-button-compact]").last().click();
      pasteInVideoInput(videoBId);

      cy.contains('add optional criteria', {matchCase: false}).click();

      cy.get('#slider_expert_largely_recommended').within(() => {
        cy.get('span[data-index=12]').click();
      });

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

      cy.get("[data-testid=entity-select-button-compact]").first().click();
      pasteInVideoInput(videoAId);
      cy.get("[data-testid=entity-select-button-compact]").last().click();
      pasteInVideoInput(videoAId);

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

      cy.visit(`/comparison?videoA=${videoAId}&videoB=${videoBId}`);
      cy.focused().type(username);
      cy.get('input[name="password"]').click().type('tournesol').type('{enter}');

      cy.location('search').should('contain', `uidA=yt%3A${videoAId}`)
      cy.location('search').should('contain', `uidB=yt%3A${videoBId}`)

      cy.get("[data-testid=entity-select-button-compact]").first().click();
      cy.get("[data-testid=paste-video-url]").find("[type=text]")
        .should('have.value', `yt:${videoAId}`);
      cy.get("[data-testid=entity-select-button-compact]").last().click();
      cy.get("[data-testid=paste-video-url]").find("[type=text]")
        .should('have.value', `yt:${videoBId}`);
    });

    it('auto-fills selector correctly when one of the video uses a legacy param', () => {
      const videoAId = 'u83A7DUNMHs';
      const videoBId = '6jK9bFWE--g';

      cy.visit(`/comparison?videoA=${videoAId}&uidB=yt:${videoBId}`);
      cy.focused().type(username);
      cy.get('input[name="password"]').click().type('tournesol').type('{enter}');

      cy.wait(1000);

      cy.location('search').should('contain', `uidA=yt%3A${videoAId}`)
      cy.location('search').should('contain', `uidB=yt%3A${videoBId}`)

      cy.get("[data-testid=entity-select-button-compact]").first().click();
      cy.get("[data-testid=paste-video-url]").find("[type=text]")
        .should('have.value', `yt:${videoAId}`);
      cy.get("[data-testid=entity-select-button-compact]").last().click();
      cy.get("[data-testid=paste-video-url]").find("[type=text]")
        .should('have.value', `yt:${videoBId}`);
    });
  });
});
