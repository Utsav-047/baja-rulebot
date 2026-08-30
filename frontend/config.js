/**
 * BAJA RuleBot - Global Frontend Configuration
 * Centralized API backend URL resolver for local development and cloud deployments.
 */

(function () {
  // Default development and production backend endpoints
  const LOCAL_BACKEND = "http://127.0.0.1:8000";
  const PRODUCTION_BACKEND = "https://baja-rulebot-production.up.railway.app";

  function resolveBackendUrl() {
    // 1. Check if user configured a custom backend in localStorage
    const savedUrl = localStorage.getItem("baja_backend_url");
    if (savedUrl && savedUrl.trim()) {
      return savedUrl.trim().replace(/\/+$/, "");
    }

    // 2. Check if running on localhost / 127.0.0.1
    const host = window.location.hostname;
    if (host === "localhost" || host === "127.0.0.1" || host === "" || window.location.protocol === "file:") {
      return LOCAL_BACKEND;
    }

    // 3. Fallback to production URL when hosted remotely (e.g. Vercel, Netlify, GitHub Pages)
    return PRODUCTION_BACKEND;
  }

  // Set global BACKEND_URL variable
  window.BACKEND_URL = resolveBackendUrl();

  // Helper function to allow runtime override
  window.setBackendUrl = function (url) {
    if (url) {
      localStorage.setItem("baja_backend_url", url);
      window.BACKEND_URL = url;
      console.log(`[BAJA RuleBot] Backend URL updated to: ${url}`);
    } else {
      localStorage.removeItem("baja_backend_url");
      window.BACKEND_URL = resolveBackendUrl();
      console.log(`[BAJA RuleBot] Backend URL reset to default: ${window.BACKEND_URL}`);
    }
  };

  console.log(`[BAJA RuleBot] Active Backend URL: ${window.BACKEND_URL}`);
})();
