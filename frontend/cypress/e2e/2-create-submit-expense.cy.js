describe('Employee creates and submits an expense', () => {
  beforeEach(() => cy.login('arta@expenseflow.dev'));

  it('shows the meal policy error, then saves and submits', () => {
    cy.visit('/expenses/new');
    cy.contains('label', 'Project').parent().click();
    cy.get('[role=option]').contains('ALPHA').click();
    cy.get('[data-cy=amount]').type('60');
    cy.get('[data-cy=attendees]').clear().type('1');
    cy.get('[data-cy=description]').type('E2E lunch with client');
    cy.get('[data-cy=save-expense]').click();
    cy.contains('Max 25 EUR per attendee');

    cy.get('[data-cy=attendees]').clear().type('3');
    cy.get('[data-cy=save-expense]').click();
    cy.contains('DRAFT');
    cy.get('[data-cy=submit-expense]').click();
    cy.contains('Submitted for approval');
    cy.contains('SUBMITTED');
  });

  it('cannot see admin pages', () => {
    cy.visit('/admin/users');
    cy.location('pathname').should('eq', '/');
  });
});
