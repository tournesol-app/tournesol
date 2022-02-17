describe('"My rated videos" page', () => {
  it('can list and update ratings status', () => {
    cy.visit('/ratings');
    cy.focused().type("user1");
    cy.get('input[name="password"]').click().type("tournesol").type('{enter}');

    // All rated videos are listed.
    cy.contains('Showing videos 1 to 20 of 263').should('be.visible');

    // Mark all videos as public.
    cy.contains('button', 'Options', {matchCase: false}).click();
    cy.contains('button', 'Mark all as public').click();

    // Close options
    cy.contains('button', 'Options').click();
    cy.contains('Filter by visibility').should('not.exist');

    // Toggle public status of first video
    cy.contains('label', 'Public', {matchCase: false}).click();

    // Select "Private" filter and check that a single video appears on the list
    cy.contains('button', 'Options', {matchCase: false}).click();
    cy.contains('label', 'Private', {matchCase: false}).click();
    cy.contains('Showing videos 1 to 1 of 1').should('be.visible');

    // Mark all videos as public, the filter is reset and all videos are listed
    cy.contains('button', 'Mark all as public').click();
    cy.contains('Showing videos 1 to 20 of 263').should('be.visible');
  })

  it('visit ratings page with filter in URL', () => {
    cy.visit('/ratings?isPublic=false');
    cy.focused().type("user1");
    cy.get('input[name="password"]').click().type("tournesol").type('{enter}');
    cy.contains('button', 'Options', {matchCase: false}).click();
    cy.contains('label', 'Private', {matchCase: false}).within(
      () => cy.get('input[type=checkbox]').should('be.checked')
    );
  })
});
