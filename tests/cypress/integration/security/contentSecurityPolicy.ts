describe('Content Security Policy checks', () => {
  it('home page contains a minimal CSP', () => {
    /**
     * default-src: is the default fallback configuration if the browser does
     * not find a specific field in the CSP, it MUST always be none.
     *
     * base-uri: is the base URL used for all relative URLs in the document,
     * it SHOULD always be self (very particular situations could require
     * otherwise).
     *
     * object-src: prevents fetching and executing plugin resources embedded
     * using, it MUST be none if tags <applet>, <embed> or <applet> are not
     * used.
     */
    cy.visit('/');

    const csp = cy.get('head meta[http-equiv=Content-Security-Policy]');
    csp.should('exist');

    const content = csp.invoke('attr', 'content');
    content.should('contains', "base-uri 'self'");
    content.should('contains', "default-src 'none'");
    content.should('contains', "object-src 'none'");
  })
})
