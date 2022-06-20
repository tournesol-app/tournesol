describe('Recommendations page', () => {
  describe('Poll - videos', () => {
    describe('Search filters', () => {
      it('sets default languages properly and backward navigation works', () => {
        cy.visit('/');
        cy.location('pathname').should('equal', '/');
        cy.contains('Recommendations').click();
        cy.contains('Filters', {matchCase: false}).should('be.visible');
        cy.location('search').should('contain', 'language=en');
        cy.go('back');
        cy.location('pathname').should('equal', '/');
      });

      describe('Filter - upload date', () => {
        it('must propose 5 timedelta', () => {
          cy.visit('/');
          cy.contains('Recommendations').click();

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
          cy.contains('Recommendations').click();

          // The month filter must appear in the URL.
          cy.location('search').should('contain', 'date=Month');

          cy.contains('Filters', {matchCase: false}).click();
          // The month input must be checked.
          cy.contains('A month ago', {matchCase: false}).should('be.visible');
          cy.get('input[type=checkbox][name=Month]').should('be.checked');

          // Currently there is no recent video in the development data.
          cy.contains('No video corresponds to your search criterias.', {matchCase: false}).should('be.visible');
        });

        it('allows to filter: a year ago', () => {
          cy.visit('/recommendations?unsafe=true');
          cy.contains('Filters', {matchCase: false}).click();

          cy.contains('A year ago', {matchCase: false}).should('be.visible');
          cy.get('input[type=checkbox][name="Year"]').check();
          cy.get('input[type=checkbox][name="Year"]').should('be.checked');
          cy.get('input[type=checkbox][name=Month]').should('not.be.checked');

          cy.location('search').should('contain', 'date=Year');
          cy.contains('Showing videos 1 to', {matchCase: false}).should('be.visible');
          cy.contains('No video corresponds to your search criterias.', {matchCase: false}).should('not.exist');
        });

        it('shows no videos for 1 day ago', () => {
          cy.visit('/recommendations?unsafe=true');
          cy.contains('Filters', {matchCase: false}).click();
          cy.contains('A day ago', {matchCase: false}).should('be.visible');
          cy.get('input[type=checkbox][name="Today"]').check();
          cy.get('input[type=checkbox][name="Today"]').should('be.checked');
          cy.contains('No video corresponds to your search criterias.', {matchCase: false}).should('be.visible');
        });

        it('allows to filter: all time', () => {
          cy.visit('/recommendations?unsafe=true');
          cy.contains('Filters', {matchCase: false}).click();

          cy.contains('A year ago', {matchCase: false}).should('be.visible');
          cy.get('input[type=checkbox][name=""]').check();
          cy.get('input[type=checkbox][name=""]').should('be.checked');
          cy.get('input[type=checkbox][name=Month]').should('not.be.checked');

          cy.contains('Showing videos 1 to 20 of', {matchCase: false}).should('be.visible');
          cy.contains('No video corresponds to your search criterias.', {matchCase: false}).should('not.exist');
        })
      });
    });
    describe('List of recommendations', () => {
      it('entities\'s thumbnails are clickable', () => {
        cy.visit('/recommendations?unsafe=true&date=');

        const thumbnail = cy.get('img.entity-thumbnail').first();
        thumbnail.click();
        cy.location('pathname').should('match', /^\/entities\//);
      });

      it('entities\'s titles are clickable', () => {
        cy.visit('/recommendations?unsafe=true&date=');

        const videoCard = cy.get('div[data-testid=video-card-info]').first();
        videoCard.find('h6').click();
        cy.location('pathname').should('match', /^\/entities\//);
      });
    });
  });
});
