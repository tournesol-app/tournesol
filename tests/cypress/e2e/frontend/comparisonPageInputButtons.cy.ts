describe('Comparison page w/ criteria buttons', () => {
  const username = "test-comp-input-buttons";
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

  before(() => {
    cy.recreateUser(username, `${username}@example.com`, "tournesol");
    createComparisons();
  });

  after(() => {
    deleteComparisons();
  });

  it('display the criteria buttons and navigation', () => {
    cy.visit(`/comparison?uidA=${ids1[0]}&uidB=${ids1[1]}&debugInput=buttons`);
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

    cy.get('button[aria-label="Next quality criterion"]').click();
    cy.contains('resilience to backfiring risks', {matchCase: false}).should('be.visible');

    cy.get('button[aria-label="Next quality criterion"]').click();
    cy.contains('should be largely recommended', {matchCase: false}).should('be.visible');

    cy.get('button[aria-label="Next quality criterion"]').click();
    cy.contains('reliable & not misleading', {matchCase: false}).should('be.visible');

    cy.get('button[aria-label="Next quality criterion"]').click();
    cy.contains('clear & pedagogical', {matchCase: false}).should('be.visible');

    cy.get('button[aria-label="Next quality criterion"]').click();
    cy.contains('important & actionable', {matchCase: false}).should('be.visible');

    cy.get('button[aria-label="Next quality criterion"]').click();
    cy.contains('layman-friendly', {matchCase: false}).should('be.visible');

    cy.get('button[aria-label="Next quality criterion"]').click();
    cy.contains('entertaining & relaxing', {matchCase: false}).should('be.visible');

    cy.get('button[aria-label="Next quality criterion"]').click();
    cy.contains('engaging & thought-provoking', {matchCase: false}).should('be.visible');

    cy.get('button[aria-label="Next quality criterion"]').click();
    cy.contains('diversity & inclusion', {matchCase: false}).should('be.visible');

    cy.get('button[aria-label="Next quality criterion"]').click().click().click();
    cy.contains('should be largely recommended', {matchCase: false}).should('be.visible');
  });
});
