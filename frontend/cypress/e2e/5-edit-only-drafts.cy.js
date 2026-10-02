describe('Editing is only offered for drafts', () => {
  beforeEach(() => cy.login('arta@expenseflow.dev'));

  it('sends the user back to the detail page when the expense is no longer a draft', () => {
    cy.visit('/expenses');
    cy.contains('.MuiDataGrid-row', 'SUBMITTED').click();
    cy.location('pathname').should('match', /^\/expenses\/\d+$/);
    cy.location('pathname').then((path) => cy.visit(`${path}/edit`));
    cy.contains('Only drafts can be edited');
    cy.location('pathname').should('match', /^\/expenses\/\d+$/);
  });
});
