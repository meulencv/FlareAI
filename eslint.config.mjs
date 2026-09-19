const browser = [
  "L", "document", "window", "fetch", "console", "URL", "matchMedia", "ResizeObserver",
  "setInterval", "clearInterval", "setTimeout", "clearTimeout",
  "requestAnimationFrame", "cancelAnimationFrame", "performance",
];

export default [{
  files: ["static/*.js", "test_*.mjs"],
  languageOptions: {
    ecmaVersion: "latest", sourceType: "module",
    globals: Object.fromEntries(browser.map(name => [name, "readonly"])),
  },
  rules: { "no-undef": "error", "no-unused-vars": "error" },
}];
