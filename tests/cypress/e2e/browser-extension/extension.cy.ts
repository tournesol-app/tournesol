import { onlyOn } from "@cypress/skip-test";

onlyOn("headed", () => {
  describe(
    "Tournesol extension",
    {
      browser: ["chromium", "chrome"],
      defaultCommandTimeout: 16000,
    },
    () => {
      // Accept the cookies.
      const consent = () => {
        cy.get("body").then(($body) => {
          if ($body.find("#dialog").length) {
            cy.get("#dialog button").last().click();
          }
        });
      };

      beforeEach(() => {
        cy.on("uncaught:exception", (err, runnable) => {
          // returning false here prevents Cypress from failing the test,
          // because of unrelated YouTube errors
          return false;
        });
      });


      describe("Home page", () => {
        it("shows the recommendations", () => {
          cy.visit("https://www.youtube.com");
          consent();
          cy.contains("Recommended by Tournesol").should("be.visible");

          // Reloading the page should not duplicate the Tournesol container.
          cy.reload();
          cy.get("#tournesol_container").should("have.length", 1);
        });
      });

      describe("Search page", () => {
        // We use an accented character to ensure that the search URL
        // parameter is properly decoded.
        const searchQuery = 'tournésol';

        it("shows Tournesol search results when the search is on", () => {
          cy.visit(`https://www.youtube.com/results?search_query=${searchQuery}&tournesolSearch=1`);
          consent();
          cy.contains("Recommended by Tournesol", {timeout: 20000});
        });

        it("doesn't show Tournesol search results when the search is off", () => {
          cy.visit(`https://www.youtube.com/results?search_query=${searchQuery}`);
          consent();
          cy.contains("Recommended by Tournesol").should("not.exist");
        });
      });

      describe("Video page", () => {
        it('shows the "Rate Later" and "Rate Now" buttons', () => {
          cy.visit("https://www.youtube.com/watch?v=6jK9bFWE--g");
          consent();

          // Dismiss YouTube ad if present.
          cy.get("body").then(($body) => {
            if ($body.find("button:contains('Dismiss')").length > 0) {
              cy.contains('button', 'Dismiss', {matchCase: false}).click();
            }
            cy.contains("button", "Rate Later", { matchCase: false }).should(
              "be.visible", { timeout: 20000 }
            );
            cy.contains("button", "Rate Now", { matchCase: false }).should(
              "be.visible", { timeout: 20000 }
            );
          });
        });
      });
    }
  );
});
