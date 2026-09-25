describe('Manager approval', () => {
  beforeEach(() => cy.login('besa@expenseflow.dev'));

  it('approves an expense from the queue', () => {
    cy.visit('/approvals');
    cy.contains('.MuiDataGrid-row', 'Headset').within(() => cy.contains('button', 'Approve').click());
    cy.contains('Approved');
  });

  it('is blocked by the database when the project budget would be exceeded', () => {
    cy.visit('/approvals');
    cy.contains('.MuiDataGrid-row', 'Docking station for hot desk').within(() => cy.contains('button', 'Approve').click());
    cy.contains('budget would be exceeded');
  });
});
