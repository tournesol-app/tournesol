export const scrollToTop = (behavior: ScrollBehavior | undefined = 'auto') => {
  // Adding a small delay avoids to scroll when the document is still
  // rendering.
  setTimeout(function () {
    document.querySelector('main')?.scrollTo?.({ top: 0, behavior: behavior });
  }, 80);
};

export const openTwitterPopup = (text: string) => {
  window.open(
    `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`,
    '',
    'menubar=no,toolbar=no,scrollbars=yes,height=600,width=800'
  );
};
