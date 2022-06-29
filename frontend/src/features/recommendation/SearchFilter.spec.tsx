/*
  Because of a regression in CRA v5, Typescript is wrongly enforced here
  See https://github.com/facebook/create-react-app/pull/11875
*/
// eslint-disable-next-line
// @ts-nocheck
import React from 'react';
import { ThemeProvider, StyledEngineProvider } from '@mui/material/styles';
import { theme } from 'src/theme';
import {
  render,
  screen,
  fireEvent,
  queryAllByTestId,
  queryByTestId,
  act,
  within,
} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Router } from 'react-router-dom';
import { createMemoryHistory } from 'history';
import { loadRecommendationsLanguages } from 'src/utils/recommendationsLanguages';
import { PollProvider } from 'src/hooks/useCurrentPoll';
import { PollsService } from 'src/services/openapi';

import SearchFilter from './SearchFilter';

describe('Filters feature', () => {
  let pushSpy = null;
  beforeEach(async () => {
    // Used to spy on URL parameters updates
    const history = createMemoryHistory();
    pushSpy = jest.spyOn(history, 'push');
    jest.spyOn(PollsService, 'pollsRetrieve').mockImplementation(async () => ({
      name: 'videos',
      criterias: [
        {
          name: 'criteria1',
          label: 'Criteria 1 Label',
          optional: false,
        },
        {
          name: 'criteria2',
          label: 'Criteria 2 Label',
          optional: true,
        },
        {
          name: 'criteria3',
          label: 'Criteria 3 Label',
          optional: true,
        },
      ],
    }));

    // Some context is needed by the component SearchFilter
    await act(async () => {
      render(
        <Router history={history}>
          <StyledEngineProvider injectFirst>
            <ThemeProvider theme={theme}>
              <PollProvider>
                <SearchFilter />
              </PollProvider>
            </ThemeProvider>
          </StyledEngineProvider>
        </Router>
      );
    });
  });

  function clickOnShowMore(wasClosed = true) {
    const checkboxDisplayFilters = screen.queryByLabelText('show more');
    expect(checkboxDisplayFilters).not.toBeNull();

    // aria-expanded should be set to false if the filters menu was closed, and true otherwise
    expect(checkboxDisplayFilters.getAttribute('aria-expanded')).toBe(
      (!wasClosed).toString()
    );

    fireEvent.click(checkboxDisplayFilters);

    // Now it should have changed
    expect(checkboxDisplayFilters.getAttribute('aria-expanded')).toBe(
      wasClosed.toString()
    );
  }

  function verifyFiltersPresence() {
    // Check date and safe filters presence
    const dateFilter = document.querySelector(
      '[data-testid=search-date-safe-filter]'
    );
    expect(queryAllByTestId(dateFilter, /checkbox-choice/i)).toHaveLength(6);

    // Check language filters presence
    const languageFilter = document.querySelector(
      '[data-testid=search-language-filter]'
    );
    expect(queryAllByTestId(languageFilter, 'autocomplete')).toHaveLength(1);

    // Check the duration filter presence
    expect(screen.getByTestId('filter-duration-lte')).toBeVisible();
    expect(screen.getByTestId('filter-duration-gte')).toBeVisible();

    // Check criteria filters presence
    expect(screen.getByLabelText('multiple criteria')).toBeVisible();
  }

  // Click on a date filter checkbox and verify the resulting URL parameters
  function clickOnDateCheckbox({
    checkbox,
    expectInUrl,
  }: {
    checkbox: 'Today' | 'Week' | 'Month' | 'Year' | '';
    expectInUrl: string;
  }) {
    const dateCheckbox = screen.queryByTestId('checkbox-choice-' + checkbox);
    expect(dateCheckbox).not.toBeNull();

    fireEvent.click(dateCheckbox);

    // Check that it updated the URL with the new date type filter
    // Use encodeURI to escape comas (in URL, "," => "%2C")
    expect(pushSpy).toHaveBeenLastCalledWith({
      search: 'date=' + encodeURIComponent(expectInUrl),
    });
  }

  // Select or unselect a language and verify the resulting URL parameters
  function selectLanguage({
    language,
    action = 'add',
    expectInUrl,
  }: {
    language: string;
    action: 'add' | 'remove';
    expectInUrl: string;
  }) {
    const languageFilter = queryByTestId(document, 'search-language-filter');
    const autocomplete = queryByTestId(languageFilter, 'autocomplete');
    expect(autocomplete).not.toBeNull();
    const input = within(autocomplete).getByRole('combobox');
    expect(input).not.toBeNull();

    if (action === 'add') {
      autocomplete.focus();
      userEvent.type(input, language);
      // Select the first item
      fireEvent.keyDown(autocomplete, { key: 'ArrowDown' });
      fireEvent.keyDown(autocomplete, { key: 'Enter' });
    } else if (action === 'remove') {
      const buttons = within(autocomplete).getAllByRole('button');
      const button = buttons.find((b) => b.textContent === language);
      expect(button).not.toBeUndefined();
      const removeButton = within(button).getByTestId('CancelIcon');
      fireEvent.click(removeButton);
    }

    // Check that it updated the URL with the new language filter
    // Use encodeURI to escape comas (in URL, "," => "%2C")
    expect(pushSpy).toHaveBeenLastCalledWith({
      search: 'language=' + encodeURIComponent(expectInUrl),
    });
    expect(loadRecommendationsLanguages()).toEqual(expectInUrl);
  }

  it('Can open and close the filters menu', () => {
    // Click to open the filters menu. The checks are made inside clickOnShowMore.
    clickOnShowMore();

    // Click again to close back the filters menu
    clickOnShowMore(false);
  });

  it('Check that all the filter checkboxes and sliders are present', () => {
    // Click to open the filters menu
    clickOnShowMore();

    // Check the presence of all the filters checkboxes
    verifyFiltersPresence();
  });

  it('Can only check one date filter at once', () => {
    clickOnShowMore();

    // click on the checkbox "This week", and check that the URL now contains "date=Week"
    clickOnDateCheckbox({ checkbox: 'Week', expectInUrl: 'Week' });

    // Now set it to "This Month".
    // Verify that the previous option "This week" is automatically unchecked (date="Month").
    clickOnDateCheckbox({ checkbox: 'Month', expectInUrl: 'Month' });

    // Same with "Today" and "This year"
    clickOnDateCheckbox({ checkbox: 'Today', expectInUrl: 'Today' });
    clickOnDateCheckbox({ checkbox: 'Year', expectInUrl: 'Year' });

    // Click again on "This year", and verify that there is no change in the URL
    clickOnDateCheckbox({ checkbox: 'Year', expectInUrl: 'Year' });

    // Set it to "All time", and verify that there is no filter in the URL
    clickOnDateCheckbox({ checkbox: '', expectInUrl: '' });
  });

  it('Can check multiple language filters at once', () => {
    clickOnShowMore();

    // select the language English and check that the URL contains "language=en"
    selectLanguage({ language: 'language.en', expectInUrl: 'en' });

    // select the language French and check that the URL contains "language=en,fr"
    selectLanguage({ language: 'language.fr', expectInUrl: 'en,fr' });

    // select the language German ("de"), and check that the URL contains "language=de,en,fr"
    selectLanguage({ language: 'language.de', expectInUrl: 'en,fr,de' });

    // Now remove the languages and verify that it was removed from the URL
    selectLanguage({
      action: 'remove',
      language: 'language.fr',
      expectInUrl: 'en,de',
    });
    selectLanguage({
      action: 'remove',
      language: 'language.en',
      expectInUrl: 'de',
    });
    selectLanguage({
      action: 'remove',
      language: 'language.de',
      expectInUrl: '',
    });
  });

  it('Can select a maximum duration', async () => {
    clickOnShowMore();

    const filter = screen
      .getByTestId('filter-duration-lte')
      .querySelector('input');

    await act(async () => {
      fireEvent.change(filter, { target: { value: '40' } });
      expect(pushSpy).toHaveBeenCalledTimes(0);
      await new Promise((resolve) => setTimeout(resolve, 800));
    });

    expect(pushSpy).toHaveBeenLastCalledWith({
      search: 'duration_gte=&duration_lte=40',
    });
  });

  it('Can select a minimum duration', async () => {
    clickOnShowMore();

    const filter = screen
      .getByTestId('filter-duration-gte')
      .querySelector('input');

    await act(async () => {
      fireEvent.change(filter, { target: { value: '20' } });
      expect(pushSpy).toHaveBeenCalledTimes(0);
      await new Promise((resolve) => setTimeout(resolve, 800));
    });

    expect(pushSpy).toHaveBeenLastCalledWith({
      search: 'duration_lte=&duration_gte=20',
    });
  });

  it('Can fold and unfold the multiple criteria', () => {
    clickOnShowMore();

    // By default the criteria sliders must be hidden.
    const checkbox = screen.queryByLabelText('multiple criteria');
    expect(screen.queryAllByLabelText(/neutral/i)).toHaveLength(0);
    expect(
      screen.queryByTestId('filter-criterion-slider-criteria1')
    ).not.toBeInTheDocument();
    expect(
      screen.queryByTestId('filter-criterion-slider-criteria2')
    ).not.toBeInTheDocument();
    expect(
      screen.queryByTestId('filter-criterion-slider-criteria3')
    ).not.toBeInTheDocument();

    // A click on the label must display all criteria sliders.
    fireEvent.click(checkbox);
    expect(screen.getAllByLabelText(/neutral/i)).toHaveLength(3);
    expect(
      screen.getByTestId('filter-criterion-slider-criteria1')
    ).toBeVisible();
    expect(
      screen.getByTestId('filter-criterion-slider-criteria2')
    ).toBeVisible();
    expect(
      screen.getByTestId('filter-criterion-slider-criteria3')
    ).toBeVisible();

    // An additional click on the label must hide all criteria sliders.
    fireEvent.click(checkbox);
    expect(screen.queryAllByLabelText(/neutral/i)).toHaveLength(0);
    expect(
      screen.queryByTestId('filter-criterion-slider-criteria1')
    ).not.toBeInTheDocument();
    expect(
      screen.queryByTestId('filter-criterion-slider-criteria2')
    ).not.toBeInTheDocument();
    expect(
      screen.queryByTestId('filter-criterion-slider-criteria3')
    ).not.toBeInTheDocument();
  });
});
