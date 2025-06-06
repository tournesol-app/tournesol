import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';

import { ContentBox, ContentHeader } from 'src/components';
import { useNotifications } from 'src/hooks/useNotifications';
import FAQTableOfContent from 'src/pages/faq/FAQTableOfContent';
import FAQEntryList from 'src/pages/faq/FAQEntryList';
import { BackofficeService, FAQEntry } from 'src/services/openapi';

/**
 * The FAQ page.
 *
 * If no entry is returned from the API, the page invite the users to ask
 * their questions directly on Discord.
 */
const FAQ = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const { i18n, t } = useTranslation();
  const { contactAdministrator } = useNotifications();

  const alreadyScrolled = React.useRef(false);

  const [entries, setEntries] = useState<Array<FAQEntry>>([]);
  const [displayedEntries, setDisplayedEntries] = useState<Array<string>>([]);

  const currentLang = i18n.resolvedLanguage;
  const scrollTo = new URLSearchParams(location.search).get('scrollTo');

  const displayEntry = (name: string, scroll = false) => {
    if (entries.find((entry) => entry.name === name)) {
      if (!displayedEntries.includes(name)) {
        setDisplayedEntries([...displayedEntries, name]);
      }
    }

    if (scroll === true) {
      const element = document.getElementById(name);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }

      const searchParams = new URLSearchParams();
      searchParams.append('scrollTo', name);
      navigate({ search: searchParams.toString() }, { replace: true });
    }
  };

  const hideEntry = (name: string) => {
    setDisplayedEntries(
      displayedEntries.filter((entryName) => entryName !== name)
    );
  };

  const setEntryVisibility = (name: string, visibility: boolean) => {
    if (visibility) {
      displayEntry(name);
    } else {
      hideEntry(name);
    }
  };

  /**
   * Automatically scroll to the requested anchor, after the entries has been
   * loaded.
   *
   * Performed only after the first loading thanks to the ref
   * `alreadyScrolled`.
   */
  useEffect(() => {
    // Scroll only one time.
    if (!alreadyScrolled.current) {
      if (location.hash) {
        const searchParams = new URLSearchParams();
        searchParams.append('scrollTo', location.hash.substring(1));
        navigate(
          { search: searchParams.toString(), hash: '' },
          { replace: true }
        );
      }

      // Do not scroll when it's not required.
      if (scrollTo && entries.length > 0) {
        const element = document.getElementById(scrollTo);

        if (element) {
          displayEntry(scrollTo);
          element.scrollIntoView({ behavior: 'smooth' });
          alreadyScrolled.current = true;
        }
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [entries, location.hash, scrollTo]);

  useEffect(() => {
    async function getFaqEntries() {
      try {
        const faq = await BackofficeService.backofficeFaqList({});
        if (faq.results) {
          setEntries(faq.results);
        }
      } catch (error) {
        contactAdministrator('error');
      }
    }

    getFaqEntries();
  }, [currentLang, contactAdministrator, setEntries]);

  return (
    <>
      <ContentHeader title={t('faqPage.frequentlyAskedQuestions')} />
      <ContentBox maxWidth="md">
        <FAQTableOfContent entries={entries} onEntryClick={displayEntry} />
        <FAQEntryList
          entries={entries}
          displayedEntries={displayedEntries}
          onEntryVisibilityChange={setEntryVisibility}
        />
      </ContentBox>
    </>
  );
};

export default FAQ;
