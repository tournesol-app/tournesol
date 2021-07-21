import loginReducer, {
  LoginState,
  getToken,
} from './loginSlice';

describe('login reducer', () => {
  const initialState: LoginState = {
    value: "",
    status: 'idle',
  };
  it('should handle initial state', () => {
    expect(loginReducer(undefined, { type: 'unknown' })).toEqual({
      value: "xxxx",
      status: 'idle',
    });
  });

  it('should handle getToken', () => {
    const actual = loginReducer(initialState, getToken("abcd"));
    expect(actual.value).toEqual("abcd");
  });
});
