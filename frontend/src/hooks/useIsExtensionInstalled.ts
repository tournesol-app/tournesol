import { useEffect, useState } from 'react';

// Set on the document root by the browser extension when it is installed
// (see browser-extension/src/signalExtensionPresence.js). Keep in sync.
const EXTENSION_INSTALLED_ATTRIBUTE = 'data-tournesol-extension-installed';

const isExtensionMarkerPresent = (): boolean =>
  document.documentElement.getAttribute(EXTENSION_INSTALLED_ATTRIBUTE) ===
  'true';

/**
 * Return whether the Tournesol browser extension is installed.
 *
 * The extension content script can run after React has mounted, so this hook
 * also watches for the marker attribute to appear.
 */
export const useIsExtensionInstalled = (): boolean => {
  const [isInstalled, setIsInstalled] = useState<boolean>(
    isExtensionMarkerPresent
  );

  useEffect(() => {
    if (isInstalled) {
      return;
    }

    const observer = new MutationObserver(() => {
      if (isExtensionMarkerPresent()) {
        setIsInstalled(true);
      }
    });

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: [EXTENSION_INSTALLED_ATTRIBUTE],
    });

    return () => observer.disconnect();
  }, [isInstalled]);

  return isInstalled;
};
