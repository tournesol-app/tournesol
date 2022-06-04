/**
 * Returns a lightened version of a hexadecimal color.
 *
 * Adapted from https://stackoverflow.com/a/59387478
 *
 * @param color A 6 digits hexadecimal color to lighten, that may include a leading '#'.
 * @param amount A real number representing the amount of lightness to add, for example `0.5`. A negative value will darken the color.
 * @returns A hexadecimal lightened version of the original `color`, including a leading '#'.
 */
export const lighten = (color: string, amount: number) => {
  const c = color.replace('#', '');
  const rgb = [
    parseInt(c.substring(0, 2), 16),
    parseInt(c.substring(2, 4), 16),
    parseInt(c.substring(4, 6), 16),
  ];

  let lightenedColor = '#';
  rgb.forEach((color) => {
    let newColor = Math.round(
      (255 - color) * (1 - Math.pow(Math.E, -amount)) + color
    );

    if (newColor < 0) newColor = 0;
    if (newColor > 255) newColor = 255;

    let hex = newColor.toString(16);
    if (hex.length === 1) hex = `0${hex}`;

    lightenedColor += hex;
  });
  return lightenedColor;
};
