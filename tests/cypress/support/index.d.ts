declare namespace Cypress {
  interface Chainable<Subject> {
      sql(query: string): Chainable<any>
      getEmailLink(): Chainable<string>

  }
}