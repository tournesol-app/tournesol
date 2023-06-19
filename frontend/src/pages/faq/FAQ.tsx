import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';

import { ContentBox, ContentHeader } from 'src/components';
import { useNotifications } from 'src/hooks/useNotifications';
import FAQTableOfContent from 'src/pages/faq/FAQTableOfContent';
import FAQEntryList from 'src/pages/faq/FAQEntryList';
import { FAQEntry, FaqService } from 'src/services/openapi';

/**
 * The FAQ page.
 *
 * If no entry is returned from the API, the page invite the users to ask
 * their questions directly on Discord.
 */
const FAQ = () => {
  const { hash } = useLocation();
  const history = useHistory();
  const { i18n, t } = useTranslation();
  const { contactAdministrator } = useNotifications();

  const alreadyScrolled = React.useRef(false);

  const [entries, setEntries] = useState<Array<FAQEntry>>([]);
  const [displayedEntries, setDisplayedEntries] = useState<Array<string>>([]);

  const currentLang = i18n.resolvedLanguage;

  const urlSearchParams = new URLSearchParams(window.location.search);
  const scrollTo = urlSearchParams.get('scrollTo');

  const displayEntry = (name: string) => {
    if (entries.find((entry) => entry.name === name)) {
      if (!displayedEntries.includes(name)) {
        setDisplayedEntries([...displayedEntries, name]);
      }
    }
    const element = document.getElementById(name);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
    const location = history.location;
    const searchParams = new URLSearchParams();
    searchParams.append('scrollTo', name);
    location.search = searchParams.toString();
    history.replace(location);
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
    if (hash) {
      const location = history.location;
      const searchParams = new URLSearchParams();
      searchParams.append('scrollTo', hash.substring(1));
      location.search = searchParams.toString();
      location.hash = '';
      history.replace(location);
    }

    // Do not scroll when it's not required.
    if (scrollTo && entries.length > 0) {
      // Scroll only one time.
      if (!alreadyScrolled.current) {
        const faqName = scrollTo ?? 'no_answer_found';
        const element = document.getElementById(faqName);

        if (element) {
          displayEntry(faqName);
          element.scrollIntoView({ behavior: 'smooth' });
          alreadyScrolled.current = true;
        }
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hash, entries, scrollTo]);

  useEffect(() => {
    async function getFaqEntries() {
      try {
        const faq = await FaqService.faqList({});
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
