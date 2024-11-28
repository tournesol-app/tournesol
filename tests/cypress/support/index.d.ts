declare namespace Cypress {
  interface Chainable<Subject> {
      sql(query: string): Chainable<any>
      getEmailLink(): Chainable<string>
      recreateUser(username: string, email: string, password: string): Chainable<any>
      deleteUser(username: string): Chainable<any>
      deleteOneComparisonOfUser(username: string, uidA: string, uidB: string): Chainable<any>
      deleteAllComparisonsOfUser(username: string): Chainable<any>
  }
}
