"""
Acoustic Space Weather Alert Tone Synthesizer for Mission Control HUD.
Generates browser-compatible audio alerts using HTML5 Web Audio API.
"""


def get_audio_alert_html(alert_type: str = "warning") -> str:
    """
    Returns an HTML/JavaScript snippet that generates an alert chime or siren
    using the browser Web Audio API without requiring external audio files.
    """
    if alert_type == "critical":
        # Two-tone pulsating klaxon siren for X-class or confirmed nowcast flare
        js_tone = """
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc1 = ctx.createOscillator();
        const osc2 = ctx.createOscillator();
        const gain = ctx.createGain();

        osc1.type = 'sawtooth';
        osc1.frequency.setValueAtTime(880, ctx.currentTime);
        osc1.frequency.exponentialRampToValueAtTime(440, ctx.currentTime + 0.35);

        osc2.type = 'sine';
        osc2.frequency.setValueAtTime(440, ctx.currentTime);
        osc2.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.35);

        gain.gain.setValueAtTime(0.12, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.7);

        osc1.connect(gain);
        osc2.connect(gain);
        gain.connect(ctx.destination);

        osc1.start();
        osc2.start();
        osc1.stop(ctx.currentTime + 0.7);
        osc2.stop(ctx.currentTime + 0.7);
        """
    else:
        # High-tech sci-fi ascending chime for precursor forecast warning
        js_tone = """
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const freqs = [587.33, 880.0, 1174.66]; // D5, A5, D6
        freqs.forEach((f, i) => {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(f, ctx.currentTime + i * 0.12);
            gain.gain.setValueAtTime(0.10, ctx.currentTime + i * 0.12);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.12 + 0.4);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(ctx.currentTime + i * 0.12);
            osc.stop(ctx.currentTime + i * 0.12 + 0.4);
        });
        """

    return f"""
    <script>
    try {{
        {js_tone}
    }} catch(e) {{
        console.log("Audio alert playback muted or blocked:", e);
    }}
    </script>
    """
