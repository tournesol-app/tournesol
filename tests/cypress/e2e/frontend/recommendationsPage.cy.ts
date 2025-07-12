describe('Recommendations page', () => {
  describe('Poll - videos', () => {

    describe('Pagination', () => {
      it('displays the pagination', () => {
        cy.visit('/recommendations');
        cy.contains('button', '< -10', {matchCase: false}).should('exist');
        cy.contains('button', '< -1', {matchCase: false}).should('exist');
        cy.contains('button', '+1 >', {matchCase: false}).should('exist');
        cy.contains('button', '+10 >', {matchCase: false}).should('exist');
      });
    });

    describe('Search filters', () => {
      it('sets default languages properly and backward navigation works', () => {
        cy.visit('/');
        cy.location('pathname').should('equal', '/');
        cy.visit('/recommendations');
        cy.contains('Filters', {matchCase: false}).should('be.visible');
        cy.location('search').should('contain', 'language=');
        cy.go('back');
        cy.location('pathname').should('equal', '/');
      });

      it('expand filters and backward navigation works', () => {
        cy.visit('/');
        cy.location('pathname').should('equal', '/');
        cy.visit('/recommendations');
        cy.contains('Filters', {matchCase: false}).click();
        cy.contains('Duration (minutes)', {matchCase: false}).should('be.visible');
        cy.go('back');
        cy.location('pathname').should('equal', '/');
      });

      describe('Filter - upload date', () => {
        it('must propose 5 timedelta', () => {
          cy.visit('/recommendations');

          cy.contains('Filters', {matchCase: false}).click();
          cy.contains('Uploaded', {matchCase: false}).should('be.visible');
          cy.contains('A day ago', {matchCase: false}).should('be.visible');
          cy.contains('A week ago', {matchCase: false}).should('be.visible');
          cy.contains('A month ago', {matchCase: false}).should('be.visible');
          cy.contains('A year ago', {matchCase: false}).should('be.visible');
          cy.contains('All time', {matchCase: false}).should('be.visible');
        });

        it('must filter by all time by default ', () => {
          cy.visit('/recommendations');
          cy.contains('Filters', {matchCase: false}).click();
          cy.contains('All time', {matchCase: false}).should('be.visible');
          cy.get('input[type=checkbox][name=""]').should('be.checked');
        });

        it('shows no videos for 1 day ago', () => {
          cy.visit('/recommendations?advanced=unsafe');
          cy.contains('Filters', {matchCase: false}).click();
          cy.contains('A day ago', {matchCase: false}).should('be.visible');
          cy.get('input[type=checkbox][name="Today"]').check();
          cy.get('input[type=checkbox][name="Today"]').should('be.checked');
          cy.contains('No item matches your search filters.', {matchCase: false}).should('be.visible');
        });

        it('allows to filter: a month ago', () => {
          cy.visit('/recommendations?advanced=unsafe');
          cy.contains('Filters', {matchCase: false}).click();

          cy.contains('A month ago', {matchCase: false}).should('be.visible');
          cy.contains('A month ago', {matchCase: false}).click();
          cy.get('input[type=checkbox][name=Month]').should('be.checked');
          cy.get('input[type=checkbox][name=""]').should('not.be.checked');
        });

        it('allows to filter: a year ago', () => {
          cy.visit('/recommendations?advanced=unsafe');
          cy.contains('Filters', {matchCase: false}).click();

          cy.contains('A year ago', {matchCase: false}).should('be.visible');
          cy.get('input[type=checkbox][name="Year"]').check();
          cy.get('input[type=checkbox][name="Year"]').should('be.checked');
          cy.get('input[type=checkbox][name=Month]').should('not.be.checked');

          cy.location('search').should('contain', 'date=Year');
          cy.contains('No item matches your search filters.', {matchCase: false}).should('not.exist');
        });
      });
    });
    describe('List of recommendations', () => {
      it('entities\'s thumbnails are clickable', () => {
        cy.visit('/recommendations?advanced=unsafe&date=');

        const thumbnail = cy.get('img.entity-thumbnail').first();
        thumbnail.click();
        cy.location('pathname').should('match', /^\/entities\//);
      });

      it('entities\'s titles are clickable', () => {
        cy.visit('/recommendations?advanced=unsafe&date=');

        const videoCard = cy.get('div[data-testid=video-card-info]').first();
        videoCard.find('h5').click();
        cy.location('pathname').should('match', /^\/entities\//);
      });
    });
  });
});
