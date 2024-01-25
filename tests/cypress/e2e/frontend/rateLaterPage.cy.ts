describe('Rate-later page', () => {

  beforeEach(() => {
    cy.sql("TRUNCATE tournesol_ratelater");
  })

  it('can add video to rate-later list', () => {
    cy.visit('/rate_later');
    cy.location('pathname').should('equal', '/login');
    cy.focused().type('user');
    cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
    cy.contains('0 video').should('be.visible');
    cy.get('input[placeholder="Video ID or URL"]').type('dQw4w9WgXcQ').type('{enter}');
    cy.contains('1 video').should('be.visible');
  });

  it('entities\'s thumbnails are clickable', () => {
    cy.visit('/rate_later');
    cy.location('pathname').should('equal', '/login');
    cy.focused().type('user');
    cy.get('input[name="password"]').click().type('tournesol').type('{enter}');

    cy.get('input[placeholder="Video ID or URL"]').type('2__Dd_KXuuU').type('{enter}');

    const thumbnail = cy.get('img.entity-thumbnail').first();
    thumbnail.click();
    cy.location('pathname').should('match', /^\/entities\//);
  });

  it('entities\'s titles are clickable', () => {
    cy.visit('/rate_later');
    cy.location('pathname').should('equal', '/login');
    cy.focused().type('user');
    cy.get('input[name="password"]').click().type('tournesol').type('{enter}');

    cy.get('input[placeholder="Video ID or URL"]').type('F1Hq8eVOMHs').type('{enter}');

    const videoCard = cy.get('div[data-testid=video-card-info]').first();
    videoCard.find('h5').click();
    cy.location('pathname').should('match', /^\/entities\//);
  });
});
