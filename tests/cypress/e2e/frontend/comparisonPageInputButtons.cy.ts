describe('Comparison page w/ criteria buttons', () => {
  const username = "test-comp-input-buttons";
  const ids1 = ["yt:hdAEGAwlK0M", "yt:lYXQvHhfKuM"];
  const ids2 = ["yt:sGLiSLAlwrY", "yt:or5WdufFrmI"];

  // This comparison should not be created during the setup.
  const newComparison = ["yt:sAjm3-IaRtI", "yt:IVqXKP91L4E"];

  const criteriaNames = [
    "should be largely recommended",
    "reliable & not misleading",
    "clear & pedagogical",
    "important & actionable",
    "layman-friendly",
    "entertaining & relaxing",
    "engaging & thought-provoking",
    "diversity & inclusion",
    "encourages better habits",
    "resilience to backfiring risks",
  ]

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

  const deleteComparison = (uidA: string, uidB: string) => {
    cy.sql(`
      DELETE FROM tournesol_comparisoncriteriascore
      WHERE comparison_id = (
        SELECT id
        FROM tournesol_comparison
        WHERE entity_1_id = (
          SELECT id FROM tournesol_entity WHERE uid = '${uidA}'
        ) AND entity_2_id = (
          SELECT id FROM tournesol_entity WHERE uid = '${uidB}'
        ) AND user_id = (
          SELECT id FROM core_user WHERE username = '${username}'
        )
      );
    `);

    cy.sql(`
        DELETE FROM tournesol_comparison
            WHERE entity_1_id = (
                SELECT id FROM tournesol_entity WHERE uid = '${uidA}'
            ) AND entity_2_id = (
                SELECT id FROM tournesol_entity WHERE uid = '${uidB}'
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

  before(() => {
    cy.recreateUser(username, `${username}@example.com`, "tournesol");
    createComparisons();
  });

  afterEach(() => {
    deleteComparison(newComparison[0], newComparison[1]);
  });

  after(() => {
    deleteComparisons();
  });

  it('display the criteria and navigation buttons', () => {
    cy.visit(`/comparison?uidA=${newComparison[0]}&uidB=${newComparison[1]}&debugInput=buttons`);
    cy.focused().type(username);
    cy.get('input[name="password"]').click().type('tournesol').type('{enter}');

    // The optional criteria button should not be displayed.
    cy.contains('add optional criteria', {matchCase: false}).should('not.exist');


    // 5 score buttons are displayed for the current criterion.
    cy.contains('should be largely recommended', {matchCase: false}).should('be.visible');
    cy.get('[data-criterion-input-type="score-button"]').should('have.length', 5);
    [-2, -1, 0, 1, 2].forEach((score) => {
      cy.get(`[data-criterion-input-score="${score}"]`).should('be.visible');
    });

    cy.get('[data-criterion-input-score="1"]').click();
    cy.contains('successfully submitted', {matchCase: false})
      .should('be.visible');

    cy.contains('should be largely recommended', {matchCase: false}).should('not.exist');
    cy.contains('reliable & not misleading', {matchCase: false}).should('be.visible');

    cy.get('button[aria-label="Previous quality criterion"]').click().click().click();
    cy.contains('reliable & not misleading', {matchCase: false}).should('not.exist');
    cy.contains('encourages better habits', {matchCase: false}).should('be.visible');

    [
      'resilience to backfiring risks',
      ...criteriaNames.slice(0 ,8)
    ].forEach((criterion) => {
      cy.get('button[aria-label="Next quality criterion"]').click();
      cy.contains(criterion, {matchCase: false}).should('be.visible');
    });

    cy.get('button[aria-label="Next quality criterion"]').click().click().click();
    cy.contains('should be largely recommended', {matchCase: false}).should('be.visible');
  });

  it('allows to compare with buttons', () => {
    cy.visit(`/comparison?uidA=${newComparison[0]}&uidB=${newComparison[1]}&debugInput=buttons`);
    cy.focused().type(username);
    cy.get('input[name="password"]').click().type('tournesol').type('{enter}');

    criteriaNames.forEach(() => {
      cy.get('[data-criterion-input-score="-2"]').click();
    });

    criteriaNames.forEach(() => {
      cy.get('[data-criterion-input-score="-2"][data-criterion-input-selected="true"]')
        .should('exist');
      cy.get('button[aria-label="Next quality criterion"]').click();
    });
  });
});
