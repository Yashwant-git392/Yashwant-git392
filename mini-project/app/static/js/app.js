/* SmartLibrary — progressive enhancements (vanilla JS, no dependencies) */
document.addEventListener('DOMContentLoaded', () => {
  // Auto-dismiss flash messages after 6 seconds
  document.querySelectorAll('.flash').forEach(el => {
    setTimeout(() => { el.style.opacity = '0'; el.style.transform = 'translateY(-6px)'; }, 6000);
    setTimeout(() => el.remove(), 6500);
  });

  // Live client-side ISBN sanity check on the book form
  const isbn = document.getElementById('isbn');
  if (isbn) {
    isbn.addEventListener('blur', () => {
      const clean = isbn.value.replace(/[- ]/g, '');
      isbn.setCustomValidity(clean.length === 10 || clean.length === 13 ? '' : 'ISBN must be 10 or 13 digits (ignoring hyphens).');
    });
  }

  // Character counter for search inputs
  document.querySelectorAll('input[type=search]').forEach(el => {
    el.addEventListener('input', () => el.toggleAttribute('data-filled', el.value.length > 0));
  });
});
