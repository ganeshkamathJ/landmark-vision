/**
 * Landmark Vision — Main JavaScript
 * Handles: nav scroll, hamburger, drag-and-drop upload,
 *          file preview, form submit state, smooth scroll,
 *          intersection observer animations, feather icons.
 */

document.addEventListener('DOMContentLoaded', () => {
  feather.replace();          // Render all feather icons
  initNav();
  initUpload();
  initScrollAnimations();
  initSmoothScrollCTA();

  // Clean up 'error' query parameter from the URL bar to prevent showing on refresh
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('error')) {
    const cleanUrl = window.location.pathname + window.location.hash;
    window.history.replaceState({}, document.title, cleanUrl);
  }
});

/* ── Navigation ─────────────────────────────────────────────── */
function initNav() {
  const header    = document.getElementById('site-header');
  const hamburger = document.getElementById('nav-hamburger');
  const navLinks  = document.getElementById('nav-links');

  // Sticky shadow on scroll
  const onScroll = () => {
    if (window.scrollY > 20) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  };

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Hamburger toggle
  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
      const isOpen = navLinks.classList.toggle('open');
      hamburger.setAttribute('aria-expanded', isOpen);

      // Animate hamburger lines
      const spans = hamburger.querySelectorAll('span');
      if (isOpen) {
        spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
        spans[1].style.opacity   = '0';
        spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
      } else {
        spans.forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
      }
    });

    // Close menu on outside click
    document.addEventListener('click', (e) => {
      if (!header.contains(e.target) && navLinks.classList.contains('open')) {
        navLinks.classList.remove('open');
        hamburger.setAttribute('aria-expanded', 'false');
        hamburger.querySelectorAll('span').forEach(s => {
          s.style.transform = '';
          s.style.opacity   = '';
        });
      }
    });

    // Close menu on link click
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
        hamburger.setAttribute('aria-expanded', 'false');
        hamburger.querySelectorAll('span').forEach(s => {
          s.style.transform = '';
          s.style.opacity   = '';
        });
      });
    });
  }
}

/* ── Upload / Drop Zone ─────────────────────────────────────── */
function initUpload() {
  const dropZone    = document.getElementById('drop-zone');
  const fileInput   = document.getElementById('file-input');
  const submitBtn   = document.getElementById('submit-btn');
  const preview     = document.getElementById('drop-zone-preview');
  const defaultView = document.getElementById('drop-zone-default');
  const previewImg  = document.getElementById('preview-img');
  const removeBtn   = document.getElementById('preview-remove');
  const fileInfoBar = document.getElementById('file-info-bar');
  const fileInfoName= document.getElementById('file-info-name');
  const fileInfoSize= document.getElementById('file-info-size');
  const uploadForm  = document.getElementById('upload-form');

  if (!dropZone) return;  // Not on upload page

  // Click drop zone → trigger file input
  dropZone.addEventListener('click', (e) => {
    if (e.target === removeBtn || removeBtn?.contains(e.target)) return;
    fileInput.click();
  });

  // Keyboard accessibility
  dropZone.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      fileInput.click();
    }
  });

  // Drag events
  ['dragenter', 'dragover'].forEach(evt => {
    dropZone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropZone.classList.add('drag-over');
    });
  });

  ['dragleave', 'drop'].forEach(evt => {
    dropZone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropZone.classList.remove('drag-over');
    });
  });

  dropZone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      document.getElementById('image-url-input').value = ''; // Clear URL if a real file is dropped
      fileInput.files = files;
      handleFile(files[0]);
    } else {
      // Check for URL in dragged item (dragging image from another tab)
      let url = e.dataTransfer.getData('text/uri-list') || e.dataTransfer.getData('URL');
      
      // Fallback: parse img src from text/html
      if (!url) {
        const html = e.dataTransfer.getData('text/html');
        if (html) {
          const match = html.match(/<img[^>]+src="([^">]+)"/i);
          if (match) url = match[1];
        }
      }

      if (url) {
        handleDroppedUrl(url);
      }
    }
  });

  // File input change
  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      document.getElementById('image-url-input').value = ''; // Clear URL if a real file is chosen
      handleFile(fileInput.files[0]);
    }
  });

  // Remove button
  if (removeBtn) {
    removeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      clearFile();
    });
  }

  // Form submit → show loading state
  if (uploadForm) {
    uploadForm.addEventListener('submit', (e) => {
      const urlInput = document.getElementById('image-url-input');
      const hasUrl = urlInput && urlInput.value.trim() !== '';
      if (!fileInput.files.length && !hasUrl) {
        e.preventDefault();
        return;
      }
      const btnText    = submitBtn.querySelector('.btn-text');
      const btnLoading = submitBtn.querySelector('.btn-loading');
      if (btnText && btnLoading) {
        btnText.hidden    = true;
        btnLoading.hidden = false;
        submitBtn.disabled = true;
      }
    });
  }

  function handleFile(file) {
    // Validate type
    const allowed = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
    if (!allowed.includes(file.type)) {
      showFileError('Unsupported file type. Please use JPG, PNG, WEBP, or GIF.');
      return;
    }

    // Validate size (16 MB)
    if (file.size > 16 * 1024 * 1024) {
      showFileError('File too large. Maximum size is 16 MB.');
      return;
    }

    // Read and preview
    const reader = new FileReader();
    reader.onload = (ev) => {
      previewImg.src = ev.target.result;

      defaultView.hidden = true;
      preview.hidden     = false;
      dropZone.classList.add('has-file');

      // File info bar
      fileInfoName.textContent = file.name;
      fileInfoSize.textContent = formatBytes(file.size);
      fileInfoBar.hidden = false;

      // Enable submit
      submitBtn.disabled = false;

      // Re-render feather icons inside the preview button
      feather.replace();
    };
    reader.readAsDataURL(file);
  }

  function handleDroppedUrl(url) {
    document.getElementById('image-url-input').value = url;
    fileInput.value = ''; // clear any selected file

    if (url.startsWith('file://')) {
      // Use a clean SVG placeholder since browser security blocks loading file:/// paths in browser preview
      previewImg.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 24 24" fill="none" stroke="%23a855f7" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>';
      previewImg.style.objectFit = 'contain';
      previewImg.style.background = 'rgba(255, 255, 255, 0.03)';
    } else {
      previewImg.src = url;
      previewImg.style.objectFit = 'cover';
      previewImg.style.background = 'none';
    }

    defaultView.hidden = true;
    preview.hidden     = false;
    dropZone.classList.add('has-file');

    // Show clean name in file info bar
    let cleanName = url.split('/').pop().split('?')[0];
    if (cleanName.length > 30) {
      cleanName = cleanName.substring(0, 27) + '...';
    }
    fileInfoName.textContent = cleanName || 'Dragged Web Image';
    fileInfoSize.textContent = url.startsWith('file://') ? 'Local File Link' : 'Web Link';
    fileInfoBar.hidden = false;

    submitBtn.disabled = false;
    feather.replace();
  }

  function clearFile() {
    fileInput.value   = '';
    const urlInput = document.getElementById('image-url-input');
    if (urlInput) urlInput.value = '';
    previewImg.src    = '';
    previewImg.style.objectFit = '';
    previewImg.style.background = '';
    preview.hidden    = true;
    defaultView.hidden = false;
    fileInfoBar.hidden = true;
    dropZone.classList.remove('has-file');
    submitBtn.disabled = true;
    feather.replace();
  }

  function showFileError(msg) {
    const err = document.createElement('div');
    err.className = 'flash flash--error';
    err.style.cssText = 'position:fixed;top:84px;right:20px;z-index:9999;max-width:380px;';
    err.innerHTML = `<svg style="width:18px;height:18px;flex-shrink:0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      <span>${msg}</span>
      <button onclick="this.parentElement.remove()" style="margin-left:auto;color:inherit;background:none;border:none;cursor:pointer;font-size:1.1rem">×</button>`;
    document.body.appendChild(err);
    setTimeout(() => err.remove(), 4000);
  }
}

/* ── Scroll Animations ──────────────────────────────────────── */
function initScrollAnimations() {
  const targets = document.querySelectorAll(
    '.step-card, .landmark-card, .tech-stat-card, .float-card, ' +
    '.result-name-card, .result-description-card, .result-facts-card, ' +
    '.about-block, .stack-card, .related-card'
  );

  if (!('IntersectionObserver' in window)) return;

  // Add initial state
  targets.forEach((el, i) => {
    el.style.opacity  = '0';
    el.style.transform = 'translateY(24px)';
    el.style.transition = `opacity 0.5s ease ${i * 0.05}s, transform 0.5s ease ${i * 0.05}s`;
  });

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity   = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  targets.forEach(el => observer.observe(el));
}

/* ── Smooth scroll for CTA buttons ──────────────────────────── */
function initSmoothScrollCTA() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const targetId = anchor.getAttribute('href').slice(1);
      const target   = document.getElementById(targetId);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
}

/* ── Utility ─────────────────────────────────────────────────── */
function formatBytes(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}
