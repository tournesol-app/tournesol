import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { ContentBox, ContentHeader } from 'src/components';
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
  const { i18n } = useTranslation();
  const [entries, setEntries] = useState<Array<FAQEntry>>([]);

  const currentLang = i18n.resolvedLanguage;

  useEffect(() => {
    async function getFaqEntries() {
      try {
        const faq = await FaqService.faqList({});
        if (faq.results) {
          setEntries(faq.results);
        }
      } catch (error) {
        // do something
      }
    }

    getFaqEntries();
  }, [currentLang, setEntries]);

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
