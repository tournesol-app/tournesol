import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';

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
  const { i18n } = useTranslation();
  const { contactAdministrator } = useNotifications();

  const alreadyScrolled = React.useRef(false);
  const [entries, setEntries] = useState<Array<FAQEntry>>([]);

  const currentLang = i18n.resolvedLanguage;

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
        const element = document.getElementById(hash.substring(1));
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' });
          alreadyScrolled.current = true;
        }
      }
    }
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
      <ContentHeader title="Frequently Asked Questions" />
      <ContentBox maxWidth="md">
        <FAQTableOfContent entries={entries} />
        <FAQEntryList entries={entries} />
      </ContentBox>
    </>
  );
};

export default FAQ;
