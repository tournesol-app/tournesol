export const scrollToTop = () => {
  document.querySelector('main')?.scrollTo({ top: 0 });
};

export const openTwitterPopup = (text: string) => {
  window.open(
    `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`,
    '',
    'menubar=no,toolbar=no,scrollbars=yes,height=600,width=800'
  );
};
