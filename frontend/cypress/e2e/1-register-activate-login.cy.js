describe('Registration, activation and login', () => {
  it('registers, activates by email and signs in', () => {
    const email = `e2e-${Date.now()}@expenseflow.dev`;
    cy.visit('/register');
    cy.get('[data-cy=first_name]').type('Erza');
    cy.get('[data-cy=email]').type(email);
    cy.get('[data-cy=password]').type('E2e-Strong-Pass-1');
    cy.get('[data-cy=confirm]').type('E2e-Strong-Pass-1');
    cy.get('[data-cy=register-submit]').click();
    cy.contains('Check your inbox');

    cy.lastEmailTo(email).then((body) => {
      const path = body.match(/\/activate\/[^\s]+/)[0];
      cy.visit(path);
    });
    cy.contains('Account activated');

    cy.visit('/login');
    cy.get('[data-cy=email]').type(email);
    cy.get('[data-cy=password]').type('E2e-Strong-Pass-1');
    cy.get('[data-cy=login-submit]').click();
    cy.contains('Hello, Erza');
  });

  it('rejects a wrong password', () => {
    cy.visit('/login');
    cy.get('[data-cy=email]').type('arta@expenseflow.dev');
    cy.get('[data-cy=password]').type('wrong-password');
    cy.get('[data-cy=login-submit]').click();
    cy.contains('Wrong email or password');
  });
});
