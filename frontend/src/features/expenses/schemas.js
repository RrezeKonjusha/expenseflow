import * as yup from 'yup';
import dayjs from 'dayjs';

// Mirrors backend/apps/expenses/policies.py so users see errors before submitting.
export const POLICY = { travelRatePerKm: 0.4, mealCapPerAttendee: 25, equipmentMax: 1000, maxAgeDays: 90 };

const noHtml = /^[^<>]*$/;

export const expenseSchema = yup.object({
  type: yup.string().oneOf(['MEAL', 'TRAVEL', 'EQUIPMENT']).required('Choose a type'),
  project: yup.number().typeError('Choose a project').required('Choose a project'),
  amount: yup.number().typeError('Enter an amount').moreThan(0, 'Must be more than 0').required(),
  expense_date: yup
    .string()
    .required('Pick a date')
    .test('not-future', 'Cannot be in the future', (v) => !v || !dayjs(v).isAfter(dayjs(), 'day'))
    .test(
      'not-old',
      `Older than ${POLICY.maxAgeDays} days`,
      (v) => !v || dayjs().diff(dayjs(v), 'day') <= POLICY.maxAgeDays,
    ),
  description: yup.string().max(500).matches(noHtml, 'No < or > characters').required('Describe the expense'),
  attendees: yup
    .number()
    .transform((v) => (Number.isNaN(v) ? undefined : v))
    .when('type', {
      is: 'MEAL',
      then: (s) =>
        s
          .required('Number of attendees')
          .min(1)
          .test('cap', `Max ${POLICY.mealCapPerAttendee} EUR per attendee`, function (v) {
            return !v || Number(this.parent.amount) <= v * POLICY.mealCapPerAttendee;
          }),
      otherwise: (s) => s.strip(),
    }),
  distance_km: yup
    .number()
    .transform((v) => (Number.isNaN(v) ? undefined : v))
    .when('type', {
      is: 'TRAVEL',
      then: (s) =>
        s
          .required('Distance in km')
          .moreThan(0)
          .test('cap', `Max ${POLICY.travelRatePerKm} EUR per km`, function (v) {
            return !v || Number(this.parent.amount) <= v * POLICY.travelRatePerKm;
          }),
      otherwise: (s) => s.strip(),
    }),
  destination: yup.string().when('type', {
    is: 'TRAVEL',
    then: (s) => s.required('Destination').matches(noHtml, 'No < or >'),
    otherwise: (s) => s.strip(),
  }),
  item_name: yup.string().when('type', {
    is: 'EQUIPMENT',
    then: (s) => s.required('Item name').matches(noHtml, 'No < or >'),
    otherwise: (s) => s.strip(),
  }),
  serial_no: yup.string().when('type', {
    is: 'EQUIPMENT',
    then: (s) =>
      s
        .required('Serial number')
        .test('max', `Equipment above ${POLICY.equipmentMax} EUR needs a purchase order`, function () {
          return Number(this.parent.amount) <= POLICY.equipmentMax;
        }),
    otherwise: (s) => s.strip(),
  }),
});
