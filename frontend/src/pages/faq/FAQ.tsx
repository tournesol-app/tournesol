import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';

import { ContentBox, ContentHeader } from 'src/components';
import { useNotifications } from 'src/hooks/useNotifications';
import FAQTableOfContent from 'src/pages/faq/FAQTableOfContent';
import FAQEntryList from 'src/pages/faq/FAQEntryList';
import { FAQEntry, FaqService } from 'src/services/openapi';
import { StatsProvider } from 'src/features/comparisons/StatsContext';

/**
 * The FAQ page.
 *
 * If no entry is returned from the API, the page invite the users to ask
 * their questions directly on Discord.
 */
const FAQ = () => {
  const { hash } = useLocation();
  const { i18n, t } = useTranslation();
  const { contactAdministrator } = useNotifications();

  const alreadyScrolled = React.useRef(false);

  const [entries, setEntries] = useState<Array<FAQEntry>>([]);
  const [displayedEntries, setDisplayedEntries] = useState<Array<string>>([]);

  const currentLang = i18n.resolvedLanguage;

  const displayEntry = (name: string) => {
    if (entries.find((entry) => entry.name === name)) {
      if (!displayedEntries.includes(name)) {
        setDisplayedEntries([...displayedEntries, name]);
      }
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
    // Do not scroll when it's not required.
    if (hash && entries.length > 0) {
      // Scroll only one time.
      if (!alreadyScrolled.current) {
        const faqName = hash.substring(1);
        const element = document.getElementById(faqName);

        if (element) {
          displayEntry(faqName);
          element.scrollIntoView({ behavior: 'smooth' });
          alreadyScrolled.current = true;
        }
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hash, entries]);

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
      <StatsProvider>
        <ContentHeader title={t('faqPage.frequentlyAskedQuestions')} />
        <ContentBox maxWidth="md">
          <FAQTableOfContent entries={entries} onEntryClick={displayEntry} />
          <FAQEntryList
            entries={entries}
            displayedEntries={displayedEntries}
            onEntryVisibilityChange={setEntryVisibility}
          />
        </ContentBox>
      </StatsProvider>
    </>
  );
};

export default FAQ;
