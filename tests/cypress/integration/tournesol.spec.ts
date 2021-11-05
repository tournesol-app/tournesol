describe('Tournesol basic tests', () => {
  it('loads correctly', () => {
    cy.visit('/');
    cy.contains('Tournesol').should('be.visible');
  })

  it('can login and logout', () => {
    cy.visit('/');
    cy.contains('Log in').click();
    cy.location('pathname').should('equal', '/login')
    cy.focused().type('user');
    cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
    cy.location('pathname').should('equal', '/');
    cy.contains('Log in').should('not.exist');
    cy.contains('Logout').click();
    cy.contains('Log in').should('be.visible');
  })
})


describe('Rate later list', () => {
  before(() => {
    cy.sql("TRUNCATE tournesol_videoratelater");
  })

  it('can add video to rate later list', () => {
    cy.visit('/rate_later');
    cy.location('pathname').should('equal', '/login');
    cy.focused().type('user');
    cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
    cy.contains('0 video').should('be.visible');
    cy.get('input[placeholder="Video id or URL"]').type('dQw4w9WgXcQ').type('{enter}');
    cy.contains('1 video').should('be.visible');
  })
})


describe('Account creation', () => {
  before(() => {
    cy.sql("DELETE FROM core_user where username = 'test-register'");
  })

  it('can create account', () => {
    cy.visit('/');
    cy.contains('Join us').click();
    cy.location('pathname').should('equal', '/signup');
    cy.get('input[name=email]').type('user@example.com');
    cy.get('input[name=username]').type('test-register');
    cy.get('input[name=password]').type('tourne50l');
    cy.get('input[name=password_confirm]').type('tourne50l');
    // Agree to the privacy policy
    cy.get('form input[type=checkbox]').check();
    cy.contains('Sign up').click();
    cy.contains('verification link').should('be.visible');
    cy.getEmailLink().then(verificationLink => cy.visit(verificationLink));
    cy.contains('account is now verified').should('be.visible');
    // Ensure that no other verification request is executed.
    cy.wait(500);
    cy.contains('Verification failed').should('not.exist');
  })
})

describe('Password reset flow', () => {
  before(() => {
    cy.recreateUser("test-pwreset", "test@example.com", "forgottenPassword");
  })

  it('can reset password', () => {
    cy.visit('/login');
    cy.contains('Forgot').click();
    cy.location('pathname').should('equal', '/forgot');
    cy.get('input[name=login]').type('test-pwreset').type('{enter}');
    cy.contains('email will be sent').should('be.visible');
    cy.getEmailLink().then(resetLink => cy.visit(resetLink));
    cy.contains('New password').should('be.visible');
    cy.get('input[name=password]').type('tournesol-new-password');
    cy.get('input[name=confirm_password]').type('tournesol-new-password').type('{enter}');
    cy.contains('password has been modified').should('be.visible');
    cy.location('pathname').should('equal', '/login');
    // Login with the new password
    cy.get('input[name=username]').type('test-pwreset');
    cy.get('input[name=password]').type('tournesol-new-password').type('{enter}');
    cy.contains('a[role=button]', 'test-pwreset').should('be.visible');
  })
})

describe('Update email address flow', () => {
  before(() => {
    cy.recreateUser("test-email-update", "email1@example.com", "tournesol");
  })

  it('can update email', () => {
    cy.visit('/settings/account');
    cy.focused().type('test-email-update');
    cy.get('input[name="password"]').click().type('tournesol').type('{enter}');
    cy.location('pathname').should('equal', '/settings/account');
    cy.contains('Your current email address is email1@example.com').should('be.visible');
    cy.get('input[name=email]').type('email2@example.com').type('{enter}');
    cy.contains('verification email has been sent ').should('be.visible');
    cy.getEmailLink().then(verifyLink => cy.visit(verifyLink));
    cy.contains('new email address is now verified').should('be.visible');
    cy.visit('/settings/account');
    cy.contains('Your current email address is email2@example.com').should('be.visible');
  })
});