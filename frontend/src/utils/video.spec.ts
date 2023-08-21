import { extractVideoId } from './video';

describe('video module', () => {
  describe('function - extractVideoId', () => {
    const videoId = 'lYXQvHhfKuM';
    const ytUrlPattern1 = 'https://www.youtube.com/watch?v=lYXQvHhfKuM';
    const ytUrlPattern2 =
      'https://www.youtube.com/live/lYXQvHhfKuM?feature=share';
    const ytUrlPattern3 = 'https://youtu.be/lYXQvHhfKuM';

    it('handles video id', () => {
      const id = extractVideoId(videoId);
      expect(id).toEqual(videoId);
    });

    it('handles Tournesol UID', () => {
      const id = extractVideoId(`yt:${videoId}`);
      expect(id).toEqual(videoId);
    });

    it("handles the pattern 'live'", () => {
      const id = extractVideoId(ytUrlPattern2);
      expect(id).toEqual(videoId);
    });

    it("handles the pattern 'watch'", () => {
      const id = extractVideoId(ytUrlPattern1);
      expect(id).toEqual(videoId);
    });

    it("handles the pattern 'youtu.be'", () => {
      const id = extractVideoId(ytUrlPattern3);
      expect(id).toEqual(videoId);
    });

    it("also works without the 'www' subdomain", () => {
      const id1 = extractVideoId(ytUrlPattern1.replace('://www.', '://'));
      expect(id1).toEqual(videoId);

      const id2 = extractVideoId(ytUrlPattern2.replace('://www.', '://'));
      expect(id2).toEqual(videoId);
    });
  });
});
