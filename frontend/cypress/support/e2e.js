const PASSWORD = 'Demo-Pass-2026!';

Cypress.Commands.add('login', (email, password = PASSWORD) => {
  cy.session(email, () => {
    cy.visit('/login');
    cy.get('[data-cy=email]').type(email);
    cy.get('[data-cy=password]').type(password, { log: false });
    cy.get('[data-cy=login-submit]').click();
    cy.contains('Waiting for approval');
  });
  cy.visit('/');
});

// Latest email for an address from Mailpit (dev/staging SMTP catcher)
Cypress.Commands.add('lastEmailTo', (address) =>
  cy
    .request(`${Cypress.env('mailpitUrl')}/api/v1/search?query=to:${encodeURIComponent(address)}`)
    .then((res) => cy.request(`${Cypress.env('mailpitUrl')}/api/v1/message/${res.body.messages[0].ID}`))
    .then((res) => res.body.Text),
);
