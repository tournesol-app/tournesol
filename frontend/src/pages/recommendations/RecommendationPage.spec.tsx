import React from 'react';

import { createMemoryHistory } from 'history';
import { act } from 'react-dom/test-utils';
import { Provider } from 'react-redux';
import { Router } from 'react-router-dom';
import configureStore, { MockStoreCreator } from 'redux-mock-store';
import thunk, { ThunkDispatch } from 'redux-thunk';

import { ThemeProvider } from '@mui/material/styles';
import { AnyAction } from '@reduxjs/toolkit';
import { render } from '@testing-library/react';

import { initialState } from 'src/features/login/loginSlice';
import { LoginState } from 'src/features/login/LoginState.model';
import * as RecommendationApi from 'src/features/recommendation/RecommendationApi';
import { PollProvider } from 'src/hooks/useCurrentPoll';
import RecommendationPage from 'src/pages/recommendations/RecommendationPage';
import { theme } from 'src/theme';
import {
  saveRecommendationsLanguages,
  loadRecommendationsLanguages,
} from 'src/utils/recommendationsLanguages';

const EntityList = () => null;
jest.mock('src/features/entities/EntityList', () => EntityList);

interface MockState {
  token: LoginState;
}

describe('RecommendationPage', () => {
  const mockStore: MockStoreCreator<
    MockState,
    ThunkDispatch<LoginState, undefined, AnyAction>
  > = configureStore([thunk]);

  let history: ReturnType<typeof createMemoryHistory>;
  let historySpy: ReturnType<typeof jest.spyOn>;
  let navigatorLanguagesGetter: ReturnType<typeof jest.spyOn>;
  let getRecommendedVideosSpy: ReturnType<typeof jest.spyOn>;

  beforeEach(() => {
    history = createMemoryHistory();
    historySpy = jest.spyOn(history, 'replace');
    navigatorLanguagesGetter = jest.spyOn(window.navigator, 'languages', 'get');
    getRecommendedVideosSpy = jest
      .spyOn(RecommendationApi, 'getRecommendations')
      .mockImplementation(async () => ({ count: 0, results: [] }));
  });

  const component = () => {
    const state = { token: initialState };
    const store = mockStore(state);
    render(
      <Provider store={store}>
        <Router history={history}>
          <ThemeProvider theme={theme}>
            <PollProvider>
              <RecommendationPage />
            </PollProvider>
          </ThemeProvider>
        </Router>
      </Provider>
    );
  };

  it('adds the navigator languages to the query string and stores them', async () => {
    navigatorLanguagesGetter.mockReturnValue(['fr', 'en-US']);
    await act(async () => component());

    expect(historySpy).toHaveBeenLastCalledWith({
      search: 'language=fr%2Cen',
    });
    expect(loadRecommendationsLanguages()).toEqual('fr,en');
    expect(getRecommendedVideosSpy).toHaveBeenCalledTimes(1);
    expect(getRecommendedVideosSpy).toHaveBeenLastCalledWith(
      'videos',
      20,
      '?language=fr%2Cen',
      expect.anything()
    );
  });

  it('adds the stored languages to the query string', async () => {
    navigatorLanguagesGetter.mockReturnValue(['fr', 'en-US']);
    saveRecommendationsLanguages('de');
    await act(async () => component());

    expect(historySpy).toHaveBeenLastCalledWith({
      search: 'language=de',
    });
    expect(loadRecommendationsLanguages()).toEqual('de');
    expect(getRecommendedVideosSpy).toHaveBeenCalledTimes(1);
    expect(getRecommendedVideosSpy).toHaveBeenLastCalledWith(
      'videos',
      20,
      '?language=de',
      expect.anything()
    );
  });

  it("doesn't change the languages already in the query string", async () => {
    navigatorLanguagesGetter.mockReturnValue(['fr', 'en-US']);
    saveRecommendationsLanguages('de');
    history.push({ search: 'language=fr' });
    await act(async () => component());

    expect(historySpy).not.toHaveBeenCalled();
    expect(loadRecommendationsLanguages()).toEqual('de');
    expect(getRecommendedVideosSpy).toHaveBeenCalledTimes(1);
    expect(getRecommendedVideosSpy).toHaveBeenLastCalledWith(
      'videos',
      20,
      '?language=fr',
      expect.anything()
    );
  });
});
