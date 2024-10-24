describe('Page - Top items', () => {
  describe('Poll - videos', () => {

    describe('General', () => {
      it('is accessible from the side bar', () => {
        cy.visit('/');
        cy.contains('Top videos').click();
        cy.location('pathname').should('equal', '/feed/top');
        cy.contains('Recommended by the community').should('be.visible');
      });
    });

    describe('Pagination', () => {
      it('displays the pagination', () => {
        cy.visit('/feed/top');
        cy.contains('button', '< -10', {matchCase: false}).should('exist');
        cy.contains('button', '< -1', {matchCase: false}).should('exist');
        cy.contains('button', '+1 >', {matchCase: false}).should('exist');
        cy.contains('button', '+10 >', {matchCase: false}).should('exist');
      });
    });

    describe('Action bar', () => {
      it('displays links to Search and Preferences', () => {
        cy.visit('/feed/top');

        cy.get('button[aria-label="Share button"]').should('be.visible');
        cy.get('a[data-testid="icon-link-to-search-page"]').click();
        cy.location('pathname').should('equal', '/search');

        cy.get('a[data-testid="icon-link-back-to-previous-page"]').click();

        cy.location('pathname').should('equal', '/feed/top');
        cy.get('a[data-testid="icon-link-to-preferences-page"]').click();
        cy.location('pathname').should('equal', '/login');
      });
    });


    describe('Search filters', () => {
      it('sets default languages properly and backward navigation works', () => {
        cy.visit('/');
        cy.location('pathname').should('equal', '/');
        cy.contains('Top videos').click();
        cy.contains('Filters', {matchCase: false}).should('be.visible');
        cy.location('search').should('contain', 'language=en');
        cy.go('back');
        cy.location('pathname').should('equal', '/');
      });

      it('expand filters and backward navigation works', () => {
        cy.visit('/');
        cy.location('pathname').should('equal', '/');
        cy.contains('Top videos').click();
        cy.contains('Filters', {matchCase: false}).click();
        cy.contains('Uploaded', {matchCase: false}).should('be.visible');
        cy.go('back');
        cy.location('pathname').should('equal', '/');
      });

      describe('Filter - upload date', () => {
        it('must propose 5 timedelta', () => {
          cy.visit('/feed/top');
          cy.contains('Filters', {matchCase: false}).click();
          cy.contains('Uploaded', {matchCase: false}).should('be.visible');
          cy.contains('A day ago', {matchCase: false}).should('be.visible');
          cy.contains('A week ago', {matchCase: false}).should('be.visible');
          cy.contains('A month ago', {matchCase: false}).should('be.visible');
          cy.contains('A year ago', {matchCase: false}).should('be.visible');
          cy.contains('All time', {matchCase: false}).should('be.visible');
        });

        it('must filter by month by default ', () => {
          cy.visit('/');
          cy.contains('Top videos').click();

          // The month filter must appear in the URL.
          cy.location('search').should('contain', 'date=Month');

          cy.contains('Filters', {matchCase: false}).click();
          // The month input must be checked.
          cy.contains('A month ago', {matchCase: false}).should('be.visible');
          cy.get('input[type=checkbox][name=Month]').should('be.checked');
        });

        it('allows to filter: a year ago', () => {
          cy.visit('/feed/top');
          cy.contains('Filters', {matchCase: false}).click();

          cy.contains('A year ago', {matchCase: false}).should('be.visible');
          cy.get('input[type=checkbox][name="Year"]').check();
          cy.get('input[type=checkbox][name="Year"]').should('be.checked');
          cy.get('input[type=checkbox][name=Month]').should('not.be.checked');

          cy.location('search').should('contain', 'date=Year');
          cy.contains('No item matches your search filters.', {matchCase: false}).should('not.exist');
        });

        it('shows no videos for 1 day ago', () => {
          cy.visit('/feed/top');
          cy.contains('Filters', {matchCase: false}).click();

          cy.contains('A day ago', {matchCase: false}).should('be.visible');
          cy.get('input[type=checkbox][name="Today"]').check();
          cy.get('input[type=checkbox][name="Today"]').should('be.checked');
          cy.contains('No item matches your search filters.', {matchCase: false}).should('be.visible');
        });

        it('allows to filter: all time', () => {
          cy.visit('/feed/top?advanced=unsafe');
          cy.contains('Filters', {matchCase: false}).click();

          cy.contains('A year ago', {matchCase: false}).should('be.visible');
          cy.contains('All time', {matchCase: false}).click();
          cy.get('input[type=checkbox][name=""]').should('be.checked');
          cy.get('input[type=checkbox][name=Month]').should('not.be.checked');
          cy.contains('No item matches your search filters.', {matchCase: false}).should('not.exist');
        });
      });
    });

    describe('List of recommendations', () => {
      it('entities\'s thumbnails are clickable', () => {
        cy.visit('/feed/top?date=');

        const thumbnail = cy.get('img.entity-thumbnail').first();
        thumbnail.click();
        cy.location('pathname').should('match', /^\/entities\//);
      });

      it('entities\'s titles are clickable', () => {
        cy.visit('/feed/top?date=');

        const videoCard = cy.get('div[data-testid=video-card-info]').first();
        videoCard.find('h5').click();
        cy.location('pathname').should('match', /^\/entities\//);
      });
    });
  });
});
