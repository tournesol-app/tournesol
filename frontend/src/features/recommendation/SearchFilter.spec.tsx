import React from 'react';
import { ThemeProvider } from '@material-ui/core/styles';
import { theme } from 'src/theme';
import { render, screen, fireEvent } from '@testing-library/react';
import { Router } from 'react-router-dom';
import { createMemoryHistory } from 'history';

import SearchFilter from './SearchFilter';
import { dateChoices } from './DateFilter';
import { languageChoices } from './LanguageFilter';
import { mainCriteriaNames } from 'src/utils/constants';

describe('Filters feature', () => {
  let pushSpy = null;
  beforeEach(() => {
    // Used to spy on URL parameters updates
    const history = createMemoryHistory();
    pushSpy = jest.spyOn(history, 'push');

    // Some context is needed by the component SearchFilter
    render(
      <Router history={history}>
        <ThemeProvider theme={theme}>
          <SearchFilter />
        </ThemeProvider>
      </Router>
    );
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
    // Check date filters presence
    for (const [, label] of Object.entries(dateChoices)) {
      expect(screen.queryAllByTestId('Upload date: ' + label)).toHaveLength(1);
    }

    // Check language filters presence
    for (const [, label] of Object.entries(languageChoices)) {
      expect(screen.queryAllByTestId('Language: ' + label)).toHaveLength(1);
    }

    // Check criteria filters presence
    for (const [, label] of mainCriteriaNames) {
      expect(screen.queryAllByTitle(label)).toHaveLength(1);
    }
  }

  // Click on a date filter checkbox and verify the resulting URL parameters
  function clickOnDateCheckbox({ checkbox, expectInUrl }) {
    const dateCheckbox = screen.queryByTestId(
      'Upload date: ' + dateChoices[checkbox]
    );
    expect(dateCheckbox).not.toBeNull();

    fireEvent.click(dateCheckbox);

    // Check that it updated the URL with the new date type filter
    // Use encodeURI to escape comas (in URL, "," => "%2C")
    expect(pushSpy).toHaveBeenLastCalledWith({
      search: expectInUrl ? 'date=' + encodeURIComponent(expectInUrl) : '',
    });
  }

  // Click on a language checkbox and verify the resulting URL parameters
  function clickOnLanguageCheckbox({ checkbox, expectInUrl }) {
    const languageCheckbox = screen.queryByTestId(
      'Language: ' + languageChoices[checkbox]
    );
    expect(languageCheckbox).not.toBeNull();

    fireEvent.click(languageCheckbox);

    // Check that it updated the URL with the new language filter
    // Use encodeURI to escape comas (in URL, "," => "%2C")
    expect(pushSpy).toHaveBeenLastCalledWith({
      search: expectInUrl ? 'language=' + encodeURIComponent(expectInUrl) : '',
    });
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

    // Uncheck the last option, and verify that there is no date filter in the URL
    clickOnDateCheckbox({ checkbox: 'Year', expectInUrl: '' });
  });

  it('Can check multiple language filters at once', () => {
    clickOnShowMore();

    // click on the checkbox English ("en"), and check that the URL contains "language=en"
    clickOnLanguageCheckbox({ checkbox: 'en', expectInUrl: 'en' });

    // click on the checkbox French ("fr"), and check that the URL contains "language=en,fr"
    clickOnLanguageCheckbox({ checkbox: 'fr', expectInUrl: 'en,fr' });

    // click on the checkbox German ("de"), and check that the URL contains "language=de,en,fr"
    clickOnLanguageCheckbox({ checkbox: 'de', expectInUrl: 'en,fr,de' });

    // Now remove click again on the checkboxes and verify that it was removed from the URL
    clickOnLanguageCheckbox({ checkbox: 'fr', expectInUrl: 'en,de' });
    clickOnLanguageCheckbox({ checkbox: 'en', expectInUrl: 'de' });
    clickOnLanguageCheckbox({ checkbox: 'de', expectInUrl: '' });
  });
});
