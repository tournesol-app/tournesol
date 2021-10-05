import { initialState } from './loginSlice';
import { hasValidToken } from './loginUtils';

describe('login validity', () => {
  const anHourInMS = 1000 * 60 * 60;
  const now = new Date();
  const anHourAgo = new Date(now.getTime() - anHourInMS);
  const anHourLater = new Date(now.getTime() + anHourInMS);
  it('should handle initial state', () => {
    expect(hasValidToken(initialState)).toEqual(false);
  });
  it('should handle expired token', () => {
    const expiredTokenState = { ...initialState };
    expiredTokenState.access_token = 'dummy_token';
    expiredTokenState.access_token_expiration_date = anHourAgo.toString();
    expect(hasValidToken(expiredTokenState)).toEqual(false);
  });
  it('should handle empty token', () => {
    const emptyTokenState = { ...initialState };
    emptyTokenState.access_token = '';
    emptyTokenState.access_token_expiration_date = anHourLater.toString();
    expect(hasValidToken(emptyTokenState)).toEqual(false);
  });
  it('should handle valid token', () => {
    const validTokenState = { ...initialState };
    validTokenState.access_token = 'dummy_token';
    validTokenState.access_token_expiration_date = anHourLater.toString();
    expect(hasValidToken(validTokenState)).toEqual(true);
  });
});
