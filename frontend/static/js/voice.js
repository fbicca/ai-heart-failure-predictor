// static/js/voice.js — mic azul pulsante + logs (Azure STT/TTS)
(function () {
  console.log("[voice] script carregado");
  // animação de pulso
  const style = document.createElement("style");
  style.textContent =
    "@keyframes micPulse{0%{box-shadow:0 0 0 0 rgba(37,99,235,.6);}70%{box-shadow:0 0 0 14px rgba(37,99,235,0);}100%{box-shadow:0 0 0 0 rgba(37,99,235,0);}}";
  document.head.appendChild(style);

  // container flutuante
  const wrap = document.createElement("div");
  Object.assign(wrap.style, {
    position: "fixed",
    right: "16px",
    bottom: "16px",
    zIndex: "9999",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "6px",
  });

  // botão
  const btn = document.createElement("button");
  Object.assign(btn.style, {
    width: "56px",
    height: "56px",
    borderRadius: "50%",
    border: "0",
    background: "#2563eb",
    color: "#fff",
    fontSize: "22px",
    cursor: "pointer",
    boxShadow: "0 8px 18px rgba(0,0,0,.18)",
  });
  btn.textContent = "🎤";

  // status
  const status = document.createElement("div");
  Object.assign(status.style, { fontSize: "12px", color: "#374151" });
  status.textContent = "Voz pronta";

  wrap.appendChild(btn);
  wrap.appendChild(status);
  document.body.appendChild(wrap);

  let rec = null,
    chunks = [],
    recording = false;
  const setStatus = (t) => {
    console.log("[voice] status:", t);
    status.textContent = t || "";
  };
  const setRec = (on) => {
    recording = on;
    btn.style.animation = on ? "micPulse 1.2s infinite" : "none";
  };

  async function start() {
    console.log("[voice] requisitando microfone...");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      rec = new MediaRecorder(stream);
      chunks = [];
      rec.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data);
      };
      rec.onstop = async () => {
        setStatus("Transcrevendo...");
        console.log("[voice] enviando para /transcribe...");
        const blob = new Blob(chunks, { type: "audio/webm" });
        const fd = new FormData();
        fd.append("audio", blob, "voz.webm");

        try {
          const r = await fetch("/transcribe", {
            method: "POST",
            body: fd,
            credentials: "include",
          });
          console.log("[voice] /transcribe status", r.status);
          let j = {};
          try {
            j = await r.json();
          } catch {}
          console.log("[voice] /transcribe payload", j);
          setStatus("Voz pronta");
          const recognized = ((j && j.text) || "").trim();
          if (!recognized) return;

          // tenta usar UI nativa se existir
          const input =
            document.getElementById("input") ||
            document.querySelector('input[type="text"], textarea');
          const sendBtn =
            document.getElementById("botao-enviar") ||
            document.querySelector('[data-send], button[type="submit"]');
          if (input && sendBtn) {
            try {
              input.value = recognized;
              sendBtn.click();
            } catch (e) {
              console.warn("[voice] erro ao usar UI nativa", e);
            }
          }

          // fallback: chama /chat e toca /tts
          const resp = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ msg: recognized }),
          });
          const reply = await resp.text();
          console.log("[voice] resposta do /chat:", reply);
          try {
            const t = await fetch("/tts", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              credentials: "include",
              body: JSON.stringify({ text: reply }),
            });
            console.log("[voice] /tts status", t.status);
            if (t.ok) {
              const b = await t.blob();
              const u = URL.createObjectURL(b);
              const a = new Audio(u);
              a.play().catch((e) =>
                console.warn("[voice] falha ao tocar audio", e)
              );
              a.onended = () => URL.revokeObjectURL(u);
            }
          } catch (e) {
            console.warn("[voice] erro no TTS", e);
          }
        } catch (e) {
          console.error("[voice] erro no /transcribe", e);
          setStatus("Falha ao transcrever.");
        }
      };
      rec.start();
      setRec(true);
      setStatus("Gravando...");
    } catch (e) {
      console.warn("[voice] sem permissão para microfone", e);
      setStatus("Permita o microfone");
    }
  }
  function stop() {
    try {
      rec && rec.state !== "inactive" && rec.stop();
    } catch (e) {
      console.warn("[voice] stop error", e);
    }
    setRec(false);
  }

  btn.addEventListener("click", () => {
    console.log("[voice] click mic; recording?", recording);
    if (!recording) start();
    else stop();
  });
})();
