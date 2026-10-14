// This is only a suggestion. Keep every system visible and never start a download automatically.
export function detectPlatform(device) {
  const agent = device.userAgent || "";
  const platform = device.userAgentData?.platform || device.platform || "";
  if (device.userAgentData?.mobile || /Android|iPhone|iPad|iPod|Windows Phone/i.test(agent)
      || /Android|iOS/i.test(platform)
      || (/Mac/i.test(platform) && device.maxTouchPoints > 1)) return "mobile";
  if (/CrOS/i.test(agent)) return null;
  for (const [name, pattern] of [["windows", /Win/i], ["macos", /Mac/i], ["linux", /Linux/i]]) {
    if (pattern.test(platform)) return name;
  }
  if (/Windows NT/i.test(agent)) return "windows";
  if (/Macintosh|Mac OS X/i.test(agent)) return "macos";
  if (/Linux|X11.*Linux/i.test(agent)) return "linux";
  return null;
}

if (typeof document !== "undefined") {
  const platform = detectPlatform(navigator);
  const note = document.querySelector("#device-note");
  const primary = document.querySelector("#primary-download");
  const names = { windows: "Windows", macos: "macOS", linux: "Linux" };
  const card = names[platform] && document.querySelector(`[data-platform="${platform}"]`);
  if (card && note && primary) {
    card.classList.add("recommended");
    const badge = document.createElement("span");
    badge.className = "recommendation";
    badge.textContent = "Sugerido para seu computador";
    card.prepend(badge);
    primary.href = `#download-${platform}`;
    primary.textContent = `Ver download para ${names[platform]} ↗`;
    note.textContent = `Seu navegador indica ${names[platform]}. Confira o pacote abaixo ou escolha outro sistema.`;
  } else if (platform === "mobile" && note) {
    note.textContent = "O Plervo PDF é para computadores. Escolha abaixo Windows, macOS ou Linux.";
  }
}
