describe('Settings - preferences page', () => {
  const username = "test-preferences-page";
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

  beforeEach(() => {
    cy.recreateUser(username, "test-preferences-page@example.com", "tournesol");
    createComparisons();
  });


  afterEach(() => {
    deleteComparisons();
  })

  const login = () => {
    cy.focused().type('test-preferences-page');
    cy.get('input[name="password"]').click().type("tournesol").type('{enter}');
  }

  describe('Navigation', () => {
    it('is accessible from the personal menu', () => {
      cy.visit('/login');
      login();

      cy.get('button#personal-menu-button').click();
      cy.get('#personal-menu').contains('Preferences').click();

      cy.location('pathname').should('equal', '/settings/preferences');
    });
  });

  describe('Setting - display weekly collective goal', () => {
    const fieldSelector = '#videos_comparison_ui__weekly_collective_goal_display';

    it('handles the value ALWAYS', () => {
      cy.visit('/settings/preferences');
      login();

      // Ensure the default value is ALWAYS
      cy.get(
        '[data-testid=videos_weekly_collective_goal_display]'
      ).should('have.value', 'ALWAYS');

      cy.visit('/comparison');
      cy.contains('Weekly collective goal').should('be.visible');
      cy.visit('/comparison?embed=1');
      cy.contains('Weekly collective goal').should('be.visible');
    });

    it('handles the value WEBSITE_ONLY', () => {
      cy.visit('/settings/preferences');
      login();

      cy.get(fieldSelector).click();
      cy.contains('Website only').click();
      cy.contains('Update preferences').click();

      cy.visit('/comparison');
      cy.contains('Weekly collective goal').should('be.visible');
      cy.visit('/comparison?embed=1');
      cy.contains('Weekly collective goal').should('not.exist');

    });

    it('handles the value EMBEDDED_ONLY', () => {
      cy.visit('/settings/preferences');
      login();

      cy.get(fieldSelector).click();
      cy.contains('Extension only').click();
      cy.contains('Update preferences').click();

      cy.visit('/comparison');
      cy.contains('Weekly collective goal').should('not.exist');
      cy.visit('/comparison?embed=1');
      cy.contains('Weekly collective goal').should('be.visible');
    });

    it('handles the value NEVER', () => {
      cy.visit('/settings/preferences');
      login();

      cy.get(fieldSelector).click();
      cy.contains('Never').click();
      cy.contains('Update preferences').click();

      cy.visit('/comparison');
      cy.contains('Weekly collective goal').should('not.exist');
      cy.visit('/comparison?embed=1');
      cy.contains('Weekly collective goal').should('not.exist');
    });
  });

  describe('Setting - automatically select entities', () => {
    it("by default, videos are automatically suggested", () => {
      cy.visit('/comparison');
      login();

      cy.get('button[data-testid="auto-entity-button-compact"]').should('be.visible');
      cy.get('button[data-testid="entity-select-button-compact"]').should('be.visible');
      cy.get('button[data-testid="auto-entity-button-full"]').should('not.be.visible');
      cy.get('button[data-testid="entity-select-button-full"]').should('not.be.visible');
    });

    it("when false, videos are not automatically suggested", () => {
      cy.visit('/settings/preferences');
      login();

      cy.get('[data-testid="videos_comparison__auto_select_entities"]').click();
      cy.contains('Update preferences').click();

      cy.visit('/comparison');

      cy.get('button[data-testid="auto-entity-button-compact"]').should('not.be.visible');
      cy.get('button[data-testid="entity-select-button-compact"]').should('not.be.visible');
      cy.get('button[data-testid="auto-entity-button-full"]').should('be.visible');
      cy.get('button[data-testid="entity-select-button-full"]').should('be.visible');

      cy.get('button[data-testid="auto-entity-button-full"]').first().click();
      cy.get('button[data-testid="auto-entity-button-full"]').first().should('not.be.visible');

      cy.get('[class="react-player__preview"]');
    });
  });

  describe('Setting - optional criteria display', () => {
    it('handles selecting and ordering criteria', () => {
      cy.visit('/comparison');
      login();

      cy.get('div[id="id_container_criteria_backfire_risk"]').should('not.be.visible');
      cy.get('div[id="id_container_criteria_layman_friendly"]').should('not.be.visible');


      cy.visit('/settings/preferences');
      cy.contains(
        'No criteria selected. All optional criteria will be hidden by default.'
      ).should('be.visible');

      cy.get('input[id="id_selected_optional_layman_friendly"]').click();
      cy.get('input[id="id_selected_optional_backfire_risk"]').click();
      cy.get('button[data-testid="videos_move_criterion_up_backfire_risk"]').click();
      cy.contains('Update preferences').click();

      cy.visit('/comparison');

      // The selected optional criteria should be visible...
      cy.get('div[id="id_container_criteria_backfire_risk"]').should('be.visible');
      cy.get('div[id="id_container_criteria_layman_friendly"]').should('be.visible');

      // ...and correctly ordered.
      cy.get('div[id="id_container_criteria_backfire_risk"]')
        .next().should('have.attr', 'id', 'id_container_criteria_layman_friendly');

      cy.get('div[id="id_container_criteria_reliability"]').should('not.be.visible');
    });
  });

  describe('Setting - rate-later auto removal', () => {
    it('handles changing the value', () => {
      cy.visit('/rate_later');
      login();

      cy.contains('removed after 4 comparison(s)').should('be.visible');

      cy.get('a[aria-label="Link to the preferences page"]').click();
      cy.contains('Automatic removal').click().type('{selectAll}1');
      cy.contains('Update preferences').click();

      cy.visit('/rate_later');
      cy.contains('removed after 1 comparison(s)').should('be.visible');

      cy.get('input[placeholder="Video ID or URL"]').type('nffV2ZuEy_M').type('{enter}');
      cy.contains('Your rate-later list contains 1 video').should('be.visible');

      cy.visit('/comparison?uidA=yt%3AnffV2ZuEy_M&uidB=yt%3AdQw4w9WgXcQ');
      cy.get('button').contains('submit').click();
      cy.visit('/rate_later');
      cy.contains('Your rate-later list contains 0 videos').should('be.visible');
    });
  });

  describe('Setting - upload date', () => {
    const fieldSelector = '#videos_recommendations__default_date';

    it('handles the value A month ago', () => {
      cy.visit('/settings/preferences');
      login();

      // Ensure the default value is A month ago
      cy.get(
        '[data-testid=videos_recommendations__default_date]'
      ).should('have.value', 'MONTH');

      cy.get('a[aria-label="Link to the recommendations page"]').should(
        'have.attr', 'href', '/recommendations?date=Month'
      );
    });

    it('handles the value A day ago', () => {
      cy.visit('/settings/preferences');
      login();

      cy.get(fieldSelector).click();
      cy.contains('A day ago').click();
      cy.contains('Update preferences').click();

      cy.get('a[aria-label="Link to the recommendations page"]').should(
        'have.attr', 'href', '/recommendations?date=Today&language=en'
      );
    });

    it('handles the value A week ago', () => {
      cy.visit('/settings/preferences');
      login();

      cy.get(fieldSelector).click();
      cy.contains('A week ago').click();
      cy.contains('Update preferences').click();

      cy.get('a[aria-label="Link to the recommendations page"]').should(
        'have.attr', 'href', '/recommendations?date=Week&language=en'
      );
    });

    it('handles the value A year ago', () => {
      cy.visit('/settings/preferences');
      login();

      cy.get(fieldSelector).click();
      cy.contains('A year ago').click();
      cy.contains('Update preferences').click();

      cy.get('a[aria-label="Link to the recommendations page"]').should(
        'have.attr', 'href', '/recommendations?date=Year&language=en'
      );
    });

    it('handles the value All time', () => {
      cy.visit('/settings/preferences');
      login();

      cy.get(fieldSelector).click();
      cy.contains('All time').click();
      cy.contains('Update preferences').click();

      cy.get('a[aria-label="Link to the recommendations page"]').should(
        'have.attr', 'href', '/recommendations?date=&language=en'
      );
    });
  });

  describe('Setting - unsafe', () => {
    it('handles the value false (hide)', () => {
      cy.visit('/settings/preferences');
      login();

      cy.get('[data-testid=videos_recommendations__default_unsafe]');
      cy.contains('Update preferences').click();

      cy.get('a[aria-label="Link to the recommendations page"]').should(
        'have.attr', 'href', '/recommendations?date=Month&language=en'
      );
    });

    it('handles the value true (show)', () => {
      cy.visit('/settings/preferences');
      login();

      cy.get('[data-testid=videos_recommendations__default_unsafe]').click();
      cy.contains('Update preferences').click();

      cy.get('a[aria-label="Link to the recommendations page"]').should(
        'have.attr', 'href', '/recommendations?date=Month&advanced=unsafe&language=en'
      );
    });
  });

  describe('Setting - exclude compared entities', () => {
    it('handles the value false (exclude)', () => {
      cy.visit('/settings/preferences');
      login();

      cy.get('[data-testid=videos_recommendations__default_exclude_compared_entities]');
      cy.contains('Update preferences').click();

      cy.get('a[aria-label="Link to the recommendations page"]').should(
        'have.attr', 'href', '/recommendations?date=Month&language=en'
      );
    });

    it('handles the value true (include)', () => {
      cy.visit('/settings/preferences');
      login();

      cy.get('[data-testid=videos_recommendations__default_exclude_compared_entities]')
        .click();
      cy.contains('Update preferences').click();

      cy.get('a[aria-label="Link to the recommendations page"]').should(
        'have.attr', 'href', '/recommendations?date=Month&advanced=exclude_compared&language=en'
      );
    });
  });
});
