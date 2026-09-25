describe('Admin reporting', () => {
  beforeEach(() => cy.login('admin@expenseflow.dev'));

  it('builds, saves and exports a report', () => {
    const name = `E2E report ${Date.now()}`;
    cy.visit('/reports');
    cy.get('[data-cy=run-report]').click();
    cy.contains('Total');
    cy.contains('button', 'Save report').click();
    cy.get('[data-cy=report-name]').type(name);
    cy.get('[data-cy=save-report]').click();
    cy.contains('Report saved');
    cy.contains(name).click();
    cy.get('[data-cy=export-xlsx]').click();
    cy.readFile(`cypress/downloads`, { timeout: 10000 }).should('exist');
  });

  it('runs the reimbursement stored procedure', () => {
    cy.visit('/reports');
    cy.get('[data-cy=reimburse]').click();
    cy.contains('expenses reimbursed');
  });

  it('shows the audit trail', () => {
    cy.visit('/admin/audit');
    cy.contains('LOGIN');
  });
});
