// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom/extend-expect';
import { MockTrans } from './mockI18next.setup';

jest.mock('react-i18next', () => ({
  // this mock makes sure any components using the `useTranslation`
  // hook can use it without a warning being shown
  useTranslation: () => {
    return {
      t: (str) => str,
      i18n: {
        changeLanguage: () => new Promise(() => null),
        resolvedLanguage: 'en',
      },
    };
  },
  Trans: MockTrans,
  initReactI18next: { type: '3rdParty', init: jest.fn() },
}));
