import { useEffect } from 'react';
import { DEFAULT_DOCUMENT_TITLE } from 'src/utils/constants';

export const useDocumentTitle = (pageTitle: string) => {
  useEffect(() => {
    document.title = pageTitle;
  }, [pageTitle]);

  useEffect(() => {
    return () => {
      document.title = DEFAULT_DOCUMENT_TITLE;
    };
  }, []);
};
