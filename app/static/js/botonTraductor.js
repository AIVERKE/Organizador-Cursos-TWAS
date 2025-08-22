// boton traductor 
(function() {
  const root = document.documentElement; // <html>
  const btn = document.getElementById('btnLang');

  // Persistir preferencia
  const saved = localStorage.getItem('lang') || 'es';
  setLang(saved);

  btn?.addEventListener('click', () => {
    const next = root.classList.contains('lang-es') ? 'en' : 'es';
    setLang(next);
  });

  function setLang(code) {
    root.classList.toggle('lang-es', code === 'es');
    root.classList.toggle('lang-en', code === 'en');
    localStorage.setItem('lang', code);
  }
})();
