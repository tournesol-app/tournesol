export const scrollToTop = (behavior: ScrollBehavior | undefined = 'auto') => {
  document.querySelector('main')?.scrollTo?.({ top: 0, behavior: behavior });
};

export const openTwitterPopup = (text: string) => {
  window.open(
    `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`,
    '',
    'menubar=no,toolbar=no,scrollbars=yes,height=600,width=800'
  );
};
