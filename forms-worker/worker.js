/**
 * North Peak Recovery form backend.
 * POST /api/submissions from northpeakrecovery.com lead forms.
 * Emails the inbox in env.FORM_INBOX after validation and a honeypot check.
 */
import { EmailMessage } from "cloudflare:email";

const ORIGINS = new Set([
  "https://northpeakrecovery.com",
  "https://www.northpeakrecovery.com"
]);
const FORMS = {
  c: "Check my funds",
  "consultation-post-sale": "Free consultation (after a sale)",
  "consultation-pre-sale": "Free consultation (before a sale)"
};
const EMAIL_RE = /^[^\s@<>"(),;:]+@[^\s@<>"(),;:]+\.[A-Za-z]{2,}$/;
const MAX_PER_IP_PER_HOUR = 8;
const hits = new Map();

function cors(origin) {
  const allow = ORIGINS.has(origin) ? origin : "https://northpeakrecovery.com";
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    "Cache-Control": "no-store"
  };
}

function json(body, status, origin) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...cors(origin) }
  });
}

function line(v, max) {
  return String(v ?? "")
    .replace(/[\u0000-\u001f\u007f]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, max);
}

function allValues(fd, name, maxEach, maxJoin) {
  return fd
    .getAll(name)
    .map((v) => line(v, maxEach))
    .filter(Boolean)
    .slice(0, 6)
    .join(", ")
    .slice(0, maxJoin);
}

function rateLimited(ip) {
  const now = Date.now();
  const hour = 60 * 60 * 1000;
  const list = (hits.get(ip) || []).filter((t) => now - t < hour);
  if (list.length >= MAX_PER_IP_PER_HOUR) {
    hits.set(ip, list);
    return true;
  }
  list.push(now);
  hits.set(ip, list);
  return false;
}

function mountain(iso) {
  try {
    return new Date(iso).toLocaleString("en-US", {
      timeZone: "America/Denver",
      dateStyle: "medium",
      timeStyle: "long"
    });
  } catch (e) {
    return "";
  }
}

function b64(s) {
  const bytes = new TextEncoder().encode(s);
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin);
}
const encWord = (s) => (/^[\x20-\x7e]*$/.test(s) ? s : `=?UTF-8?B?${b64(s)}?=`);
const wrap76 = (s) => s.replace(/.{1,76}/g, "$&\r\n");

function mime({ from, fromName, to, subject, replyTo, replyName, text, id }) {
  const headers = [
    `From: ${encWord(fromName)} <${from}>`,
    `To: <${to}>`,
    replyTo ? `Reply-To: ${replyName ? `"${encWord(replyName.replace(/["\\]/g, ""))}" ` : ""}<${replyTo}>` : null,
    `Subject: ${encWord(subject)}`,
    `Date: ${new Date().toUTCString()}`,
    `Message-ID: <${id}@northpeakrecovery.com>`,
    "MIME-Version: 1.0",
    'Content-Type: text/plain; charset="UTF-8"',
    "Content-Transfer-Encoding: base64"
  ].filter(Boolean);
  return headers.join("\r\n") + "\r\n\r\n" + wrap76(b64(text));
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors(origin) });
    }
    if (request.method !== "POST") {
      return json({ ok: false, error: "method" }, 405, origin);
    }
    if (origin && !ORIGINS.has(origin)) {
      return json({ ok: false, error: "origin" }, 403, origin);
    }

    const ip = request.headers.get("CF-Connecting-IP") || "";
    if (ip && rateLimited(ip)) {
      return json({ ok: false, error: "rate" }, 429, origin);
    }

    let fd;
    try {
      fd = await request.formData();
    } catch (e) {
      return json({ ok: false, error: "body" }, 400, origin);
    }

    // Honeypot: pretend success, do not email.
    if (line(fd.get("company"), 200)) {
      return json({ ok: true }, 200, origin);
    }

    const form = line(fd.get("form"), 40);
    const name = line(fd.get("name"), 120);
    const email = line(fd.get("email"), 200).toLowerCase();
    const phone = line(fd.get("phone"), 40);
    const address = line(fd.get("address"), 200);
    const county = line(fd.get("county"), 80);
    const state = line(fd.get("state"), 80);
    const saleYear = line(fd.get("sale_year"), 20);
    const contactPref = line(fd.get("contact_pref"), 40);
    const consent = line(fd.get("consent"), 10);
    const saleType = allValues(fd, "sale_type", 40, 120);
    const bestTime = allValues(fd, "best_time", 40, 120);
    const page = line(fd.get("page"), 200);
    const source = line(fd.get("source"), 40);
    const digits = phone.replace(/\D/g, "").length;

    const errors = [];
    if (!FORMS[form]) errors.push("form");
    if (name.length < 1) errors.push("name");
    if (!EMAIL_RE.test(email)) errors.push("email");
    if (digits > 0 && (digits < 10 || digits > 15)) errors.push("phone");
    if (digits >= 10 && form.startsWith("consultation-") && consent !== "yes") errors.push("consent");
    if (form === "c" && consent !== "yes") errors.push("consent");
    if (errors.length) return json({ ok: false, error: "invalid", fields: errors }, 422, origin);

    const to = env.FORM_INBOX;
    const from = env.FROM_ADDR;
    const id = crypto.randomUUID();
    const receivedAt = new Date().toISOString();
    const subject = `${FORMS[form]}: ${name}`;
    const rows = [
      ["Form", FORMS[form]],
      ["Name", name],
      ["Email", email],
      ["Phone", phone],
      ["Property address", address],
      ["State", state],
      ["County", county],
      ["Sale year", saleYear],
      ["Type of sale", saleType],
      ["Best time to reach you", bestTime],
      ["Contact preference", contactPref],
      ["Consent", consent || "not checked"],
      ["Page", page],
      ["Source", source]
    ]
      .filter(([, v]) => v)
      .map(([k, v]) => `${k}: ${v}`);

    const text = [
      `New ${FORMS[form]} from northpeakrecovery.com`,
      "",
      ...rows,
      "",
      `Submission ID: ${id}`,
      `Received (UTC): ${receivedAt}`,
      `Received (Mountain Time): ${mountain(receivedAt)}`,
      `IP country: ${request.headers.get("CF-IPCountry") || "(unknown)"}`,
      "",
      "Reply to this email to answer the person directly."
    ].join("\n");

    const raw = mime({
      from,
      fromName: "North Peak Recovery website",
      to,
      subject,
      replyTo: email,
      replyName: name,
      text,
      id
    });

    try {
      await env.SEND_EMAIL.send(new EmailMessage(from, to, raw));
    } catch (e) {
      return json({ ok: false, error: "send" }, 502, origin);
    }
    return json({ ok: true, id }, 200, origin);
  }
};
