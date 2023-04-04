import { onlyOn } from "@cypress/skip-test";

onlyOn("headed", () => {
  describe(
    "Tournesol extension",
    {
      browser: ["chromium", "chrome"],
      defaultCommandTimeout: 32000,
    },
    () => {
      const consent = () => {
        cy.get("body").then(($body) => {
          // Agree to cookies dialog if it's present
          if ($body.find("#dialog").length) {
            cy.get(
              "#dialog .yt-spec-button-shape-next.yt-spec-button-shape-next--filled.yt-spec-button-shape-next--call-to-action.yt-spec-button-shape-next--size-m"
            )
              .last()
              .click();
          }
        });
      };

      beforeEach(() => {
        cy.on("uncaught:exception", (err, runnable) => {
          // returning false here prevents Cypress from
          // failing the test, because of unrelated Youtube errors
          return false;
        });
      });

      it("shows Tournesol recommendations on youtube.com", () => {
        cy.visit("https://www.youtube.com");
        consent();
        cy.contains("Recommended by Tournesol").should("be.visible");
        cy.get("#tournesol_title:contains(Recommended by Tournesol)").should(
          "have.length",
          1
        );
      });

      it("does not show Tournesol recommendations on youtube.com/results when search is off", () => {
        cy.visit("https://www.youtube.com/results?search_query=guerre");
        consent();
        cy.contains("Recommended by Tournesol").should("not.exist");
      });

      it("shows Tournesol recommendations on youtube.com/results when search is on", () => {
        cy.visit("http://localhost:3000/");

        cy.origin("https://www.youtube.com/", function () {
          cy.visit("https://www.youtube.com/");

          // consent to youtube and turn the search on before resume
          cy.pause();

          cy.visit("https://www.youtube.com/results?search_query=test");

          cy.contains("Recommended by Tournesol");
        });
      });

      it('shows "Rate later" and "Rate Now" button on video page', () => {
        cy.visit("https://www.youtube.com/");
        consent();
        cy.visit("https://www.youtube.com/watch?v=6jK9bFWE--g");

        cy.get("body").then(($body) => {
          if ($body.find("button:contains('Dismiss')").length > 0) {
            // Dismiss Youtube Ad if present
            cy.contains("button", "Dismiss", { matchCase: false }).click();
          }
          cy.contains("button", "Rate Later", { matchCase: false }).should(
            "be.visible"
          );
          cy.contains("button", "Rate Now", { matchCase: false }).should(
            "be.visible"
          );
        });
      });
    }
  );
});
