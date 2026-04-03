importScripts("https://cdn.jsdelivr.net/npm/diff@7/dist/diff.min.js");

self.onmessage = function (e) {
  const { original, revised, id } = e.data;
  try {
    const changes = Diff.diffWords(original, revised);
    self.postMessage({ changes, id });
  } catch (err) {
    self.postMessage({ error: String(err), id });
  }
};
