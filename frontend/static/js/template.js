const isDev = window.location.hostname === "127.0.0.1";

API_BASE = isDev
  ? "http://127.0.0.1:5000/"
  : "https://alottakeys.xyz/";