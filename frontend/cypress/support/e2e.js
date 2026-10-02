const PASSWORD = 'Demo-Pass-2026!';

// Logs in through the API (the login form itself is covered in spec 1).
// cy.session is not used: it would restore a refresh cookie that rotation has already blacklisted.
Cypress.Commands.add('login', (email, password = PASSWORD) => {
  cy.request('POST', '/api/v1/auth/login/', { email, password });
  // Wait for the dashboard: the refresh call must finish before the next cy.visit,
  // otherwise the rotated refresh cookie is lost with the aborted request.
  cy.visit('/');
  cy.contains('Waiting for approval');
});

// Latest email for an address from Mailpit (dev/staging SMTP catcher).
// Emails are sent by the Celery worker, so poll until the message arrives.
Cypress.Commands.add('lastEmailTo', (address, attempts = 20) =>
  cy
    .request(`${Cypress.env('mailpitUrl')}/api/v1/search?query=to:${encodeURIComponent(address)}`)
    .then((res) => {
      if (res.body.messages.length) {
        return cy
          .request(`${Cypress.env('mailpitUrl')}/api/v1/message/${res.body.messages[0].ID}`)
          .then((msg) => msg.body.Text);
      }
      if (attempts <= 1) throw new Error(`No email to ${address} arrived in Mailpit`);
      cy.wait(500);
      return cy.lastEmailTo(address, attempts - 1);
    }),
);
