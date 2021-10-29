declare namespace Cypress {
  interface Chainable<Subject> {
      sql(query: string): Chainable<any>
      getEmailLink(): Chainable<string>
      recreateUser(username: string, email: string, password: string): Chainable<any>
  }
}