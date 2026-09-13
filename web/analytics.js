window.FCAnalytics = (() => {
  const cfg = window.FC_CONFIG || {};
  let ready = false;

  function init() {
    if (cfg.analyticsProvider === "goatcounter" && cfg.goatCounterCode) {
      const s = document.createElement("script");
      s.async = true;
      s.src = "//gc.zgo.at/count.js";
      s.dataset.goatcounter = `https://${cfg.goatCounterCode}.goatcounter.com/count`;
      s.onload = () => { ready = true; };
      document.head.appendChild(s);
    }
  }

  function event(name, props={}) {
    // Never send free-text search queries or personal-fit slider values.
    if (!ready || !window.goatcounter || typeof window.goatcounter.count !== "function") return;
    const safe = Object.entries(props)
      .filter(([k,v]) => ["soc","count","surface"].includes(k) && v != null)
      .map(([k,v]) => `${k}=${String(v).slice(0,40)}`).join("&");
    window.goatcounter.count({
      path: `/event/${name}${safe ? "?" + safe : ""}`,
      title: `event:${name}`,
      event: true
    });
  }

  init();
  return { event };
})();
