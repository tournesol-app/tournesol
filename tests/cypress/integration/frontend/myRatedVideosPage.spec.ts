describe('My rated elements page', () => {
  describe('Poll - videos', () => {
    it('can list and update ratings status', () => {
      cy.visit('/ratings');
      cy.focused().type("user1");
      cy.get('input[name="password"]').click().type("tournesol").type('{enter}');

      // All rated videos are listed.
      cy.contains(/Showing videos 1 to 20 of \d+/).should('be.visible');

      // Mark all videos as public.
      cy.contains('button', 'Options', {matchCase: false}).click();
      cy.contains('Filter by visibility').should('be.visible');
      cy.contains('button', 'Mark all as public').click();

      // Close options
      cy.contains('button', 'Options').click();
      cy.contains('Order by').should('not.exist');

      // Toggle public status of first video
      cy.contains('label', 'Public', {matchCase: false}).click();

      // Select "Private" filter and check that a single video appears on the list
      cy.contains('button', 'Options', {matchCase: false}).click();
      cy.contains('label', 'Private', {matchCase: false}).click();
      cy.contains('Showing videos 1 to 1 of 1').should('be.visible');

      // Mark all videos as public, the filter is reset and all videos are listed
      cy.contains('button', 'Mark all as public').click();
      cy.contains(/Showing videos 1 to 20 of \d+/).should('be.visible');
    });

    it('visit ratings page with `isPublic` param in URL', () => {
      cy.visit('/ratings?isPublic=false');
      cy.focused().type("user1");
      cy.get('input[name="password"]').click().type("tournesol").type('{enter}');
      cy.contains('button', 'Options', {matchCase: false}).click();
      cy.contains('label', 'Private', {matchCase: false}).within(
        () => cy.get('input[type=checkbox]').should('be.checked')
      );
    });

    it('entities\'s thumbnails are clickable', () => {
      cy.visit('/ratings');
      cy.focused().type("user1");
      cy.get('input[name="password"]').click().type("tournesol").type('{enter}');

      const thumbnail = cy.get('img.entity-thumbnail').first();
      thumbnail.click();
      cy.location('pathname').should('match', /^\/entities\//);
    });

    it('entities\'s titles are clickable', () => {
      cy.visit('/ratings');
      cy.focused().type("user1");
      cy.get('input[name="password"]').click().type("tournesol").type('{enter}');

      const videoCard = cy.get('div[data-testid=video-card-info]').first();
      videoCard.find('h6').click();
      cy.location('pathname').should('match', /^\/entities\//);
    });

    describe('ratings ordering', () => {
      // Generic parameter available for all entity types.
      const lastComparedAtLabel = "Last comparison date";
      const nComparisonsLabel = "Number of comparisons";

      // Video specific metadata.
      const durationLabel = "Duration";
      const publicationDateLabel = "Publication date";

      it('the ratings can be order by `last_compared_at`', () => {
        cy.visit('/ratings');
        cy.focused().type("user1");
        cy.get('input[name="password"]').click().type("tournesol").type('{enter}');

        cy.contains('button', 'Options', {matchCase: false}).click();
        cy.contains('Order by').should('be.visible');

        // Ascending order.
        cy.get('div[id=order-by-metadata]').click();
        cy.get('li[data-value=last_compared_at]').click();
        cy.location().should((loc) => {
          expect(loc.search).to.eq('?orderBy=last_compared_at')
        });

        // Descending order.
        cy.get('div[id=order-by-metadata]').click();
        cy.get('li[data-value=-last_compared_at]').click();
        cy.location().should((loc) => {
          expect(loc.search).to.eq('?orderBy=-last_compared_at')
        });
      });

      it('the ratings can be order by `n_comparisons`', () => {
        cy.visit('/ratings');
        cy.focused().type("user1");
        cy.get('input[name="password"]').click().type("tournesol").type('{enter}');

        cy.contains('button', 'Options', {matchCase: false}).click();
        cy.contains('Order by').should('be.visible');

        // Ascending order.
        cy.get('div[id=order-by-metadata]').click();
        cy.get('li[data-value=n_comparisons]').click();
        cy.location().should((loc) => {
          expect(loc.search).to.eq('?orderBy=n_comparisons')
        });

        cy.contains('1 comparison by you').should('be.visible');

        // Descending order.
        cy.get('div[id=order-by-metadata]').click();
        cy.get('li[data-value=-n_comparisons]').click();
        cy.location().should((loc) => {
          expect(loc.search).to.eq('?orderBy=-n_comparisons')
        });

        cy.contains('28 comparisons by you').should('be.visible');
      });

      it('the ratings can be order by video specific metadata fields', () => {
        cy.visit('/ratings');
        cy.focused().type("user1");
        cy.get('input[name="password"]').click().type("tournesol").type('{enter}');
    
        cy.contains('button', 'Options', {matchCase: false}).click();
        cy.contains('Order by').should('be.visible');

        // Ascending order.
        cy.get('div[id=order-by-metadata]').click();
        cy.get('li[data-value=duration]').click();
        cy.location().should((loc) => {
          expect(loc.search).to.eq('?orderBy=duration')
        });

        // Descending order.
        cy.get('div[id=order-by-metadata]').click();
        cy.get('li[data-value=-duration]').click();
        cy.location().should((loc) => {
          expect(loc.search).to.eq('?orderBy=-duration')
        });

        // Ascending order.
        cy.get('div[id=order-by-metadata]').click();
        cy.get('li[data-value=publication_date]').click();
        cy.location().should((loc) => {
          expect(loc.search).to.eq('?orderBy=publication_date')
        });

        // Descending order.
        cy.get('div[id=order-by-metadata]').click();
        cy.get('li[data-value=-publication_date]').click();
        cy.location().should((loc) => {
          expect(loc.search).to.eq('?orderBy=-publication_date')
        });
      });

      it('visit ratings page with `orderBy` param in URL', () => {
        cy.visit('/ratings?orderBy=-last_compared_at');
        cy.focused().type("user1");
        cy.get('input[name="password"]').click().type("tournesol").type('{enter}');
        cy.contains('button', 'Options', {matchCase: false}).click();
        cy.get('input[data-testid=order-by-metadata-input]').should('have.value', '-last_compared_at');
      });
    });
  });
});
