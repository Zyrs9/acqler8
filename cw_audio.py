# cw_audio.py
# Central CW audio engine — generates and plays Morse tones using numpy + sounddevice.
# All timing follows standard Morse code ratios:
#   dit = 1 unit, dah = 3 units, inter-element gap = 1 unit,
#   inter-letter gap = 3 units, inter-word gap = 7 units.

import threading
import numpy as np

try:
    import sounddevice as sd
    _HAS_SD = True
except ImportError:
    _HAS_SD = False

# ── Defaults ───────────────────────────────────────────────────────────────────
DEFAULT_WPM   = 15          # Paris standard: 1 WPM = 1200 ms / WPM per dit
DEFAULT_FREQ  = 700         # Hz — classic CW sidetone pitch
DEFAULT_VOL   = 0.4         # 0.0 – 1.0 amplitude
SAMPLE_RATE   = 44100       # Hz

# ── Global noise settings (used by build_audio unless overridden) ──────────────
_noise_db: float  = 0.0
_qrm_freq: float  = 0.0

# ── Sidetone queue — ensures rapid Q/E presses play sequentially ───────────────
import queue as _queue

class _SidetonePlayer:
    """
    Persistent audio stream for sidetone playback.
    Keeps the sounddevice OutputStream open so there is no device-open
    latency on each keystroke — eliminates the 'first part missing' bug.
    """
    def __init__(self):
        self._q: _queue.Queue = _queue.Queue()
        self._stream = None
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _open_stream(self):
        if not _HAS_SD:
            return
        try:
            self._stream = sd.OutputStream(
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype='float32',
                blocksize=512,
            )
            self._stream.start()
            # Warm-up write: push a silent buffer so the driver is
            # fully initialised before the first real tone arrives.
            silence = np.zeros(512, dtype=np.float32)
            self._stream.write(silence)
        except Exception:
            self._stream = None

    def _run(self):
        self._open_stream()
        while True:
            audio = self._q.get()
            if audio is None:
                break
            if self._stream is not None:
                try:
                    self._stream.write(audio)
                except Exception:
                    # Stream broke — try to reopen once
                    try:
                        self._stream.close()
                    except Exception:
                        pass
                    self._open_stream()
                    try:
                        self._stream.write(audio)
                    except Exception:
                        pass
            self._q.task_done()

    def enqueue(self, audio: np.ndarray):
        # Keep queue short so the player stays responsive
        while self._q.qsize() > 3:
            try:
                self._q.get_nowait()
                self._q.task_done()
            except _queue.Empty:
                break
        self._q.put(audio)

    def clear(self):
        """Flush pending beeps (does not close the stream)."""
        while not self._q.empty():
            try:
                self._q.get_nowait()
                self._q.task_done()
            except _queue.Empty:
                break


_sidetone = _SidetonePlayer()



def set_noise(noise_db: float = 0.0, qrm_freq: float = 0.0):
    """
    Configure background noise and QRM.

    noise_db: SNR in dB.  0 = silent.  Suggested range: 5 (heavy) – 30 (light).
    qrm_freq: frequency of an interfering CW carrier in Hz.  0 = none.
    """
    global _noise_db, _qrm_freq
    _noise_db = noise_db
    _qrm_freq = qrm_freq


# ── Timing helpers ─────────────────────────────────────────────────────────────
def dit_ms(wpm: int) -> float:
    """Duration of one dit in milliseconds."""
    return 1200.0 / wpm


def _tone(duration_ms: float, freq: float, vol: float) -> np.ndarray:
    """Generate a sine-wave tone with short fade in/out to avoid clicks."""
    n = int(SAMPLE_RATE * duration_ms / 1000)
    t = np.linspace(0, duration_ms / 1000, n, endpoint=False)
    wave = (vol * np.sin(2 * np.pi * freq * t)).astype(np.float32)
    # 5 ms fade in / out
    fade = int(SAMPLE_RATE * 0.005)
    if fade * 2 < n:
        wave[:fade]  *= np.linspace(0, 1, fade, dtype=np.float32)
        wave[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)
    return wave


def _silence(duration_ms: float) -> np.ndarray:
    """Generate silence of given duration."""
    n = int(SAMPLE_RATE * duration_ms / 1000)
    return np.zeros(n, dtype=np.float32)


def _apply_noise(audio: np.ndarray,
                 noise_db: float,
                 qrm_freq: float) -> np.ndarray:
    """Mix white noise and/or a QRM carrier into an audio array."""
    if len(audio) == 0:
        return audio
    result = audio.copy()
    n = len(audio)

    if noise_db > 0:
        # Signal power
        sig_power = float(np.mean(audio ** 2)) or 1e-6
        # Noise power from SNR: SNR_dB = 10*log10(P_sig/P_noise)
        noise_power = sig_power / (10 ** (noise_db / 10))
        noise = np.random.normal(0, np.sqrt(noise_power), n).astype(np.float32)
        result += noise

    if qrm_freq > 0:
        t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
        carrier_amp = float(np.max(np.abs(audio))) * 0.35
        result += (carrier_amp * np.sin(2 * np.pi * qrm_freq * t)).astype(np.float32)

    # Normalise to [-1, 1]
    peak = np.max(np.abs(result))
    if peak > 1.0:
        result /= peak
    return result


# ── Public API ────────────────────────────────────────────────────────────────
def build_audio(morse_string: str,
                wpm: int = DEFAULT_WPM,
                freq: float = DEFAULT_FREQ,
                vol: float = DEFAULT_VOL,
                farnsworth_wpm: int = 0,
                noise_db: float | None = None,
                qrm_freq: float | None = None) -> np.ndarray:
    """
    Convert a Morse string (dots, dashes, spaces) to a numpy audio array.

    morse_string: e.g. '.- -... -.-.', spaces separate letters, ' / ' words
    farnsworth_wpm: if > 0, dit/dah timing uses this WPM for character speed,
                    but inter-letter/word gaps are stretched to the slower `wpm`.
    noise_db / qrm_freq: override global noise settings if provided.
    """
    char_wpm = farnsworth_wpm if farnsworth_wpm > wpm else wpm
    dit  = dit_ms(char_wpm)
    gap_el   = dit                      # inter-element
    gap_let  = dit_ms(wpm) * 3         # inter-letter  (Farnsworth stretches this)
    gap_word = dit_ms(wpm) * 7         # inter-word

    segments: list[np.ndarray] = []

    words = morse_string.strip().split(' / ')
    for wi, word in enumerate(words):
        letters = word.strip().split(' ')
        for li, letter in enumerate(letters):
            for ei, element in enumerate(letter):
                if element == '.':
                    segments.append(_tone(dit, freq, vol))
                elif element == '-':
                    segments.append(_tone(dit * 3, freq, vol))
                if ei < len(letter) - 1:
                    segments.append(_silence(gap_el))
            if li < len(letters) - 1:
                segments.append(_silence(gap_let))
        if wi < len(words) - 1:
            segments.append(_silence(gap_word))

    if not segments:
        return np.zeros(0, dtype=np.float32)

    audio = np.concatenate(segments)

    nb = _noise_db if noise_db is None else noise_db
    qf = _qrm_freq if qrm_freq is None else qrm_freq
    if nb > 0 or qf > 0:
        audio = _apply_noise(audio, nb, qf)

    return audio


def play_morse(morse_string: str,
               wpm: int = DEFAULT_WPM,
               freq: float = DEFAULT_FREQ,
               vol: float = DEFAULT_VOL,
               farnsworth_wpm: int = 0,
               blocking: bool = False) -> None:
    """Play a Morse string asynchronously (non-blocking by default)."""
    if not _HAS_SD:
        return
    audio = build_audio(morse_string, wpm, freq, vol, farnsworth_wpm)
    if len(audio) == 0:
        return
    if blocking:
        sd.play(audio, SAMPLE_RATE)
        sd.wait()
    else:
        t = threading.Thread(target=_play_blocking, args=(audio,), daemon=True)
        t.start()


def play_dit(wpm: int = DEFAULT_WPM, freq: float = DEFAULT_FREQ,
             vol: float = DEFAULT_VOL) -> None:
    """Enqueue a single dit beep to the sidetone player."""
    if not _HAS_SD:
        return
    pad   = np.zeros(int(SAMPLE_RATE * 0.005), dtype=np.float32)  # 5 ms lead-in
    tone  = _tone(dit_ms(wpm), freq, vol)
    _sidetone.enqueue(np.concatenate([pad, tone]))


def play_dah(wpm: int = DEFAULT_WPM, freq: float = DEFAULT_FREQ,
             vol: float = DEFAULT_VOL) -> None:
    """Enqueue a single dah beep to the sidetone player."""
    if not _HAS_SD:
        return
    pad   = np.zeros(int(SAMPLE_RATE * 0.005), dtype=np.float32)  # 5 ms lead-in
    tone  = _tone(dit_ms(wpm) * 3, freq, vol)
    _sidetone.enqueue(np.concatenate([pad, tone]))


def stop() -> None:
    """Flush the sidetone queue (stream stays open for next use)."""
    _sidetone.clear()


def is_available() -> bool:
    return _HAS_SD


# ── Internal ──────────────────────────────────────────────────────────────────
def _play_blocking(audio: np.ndarray) -> None:
    """
    Play audio synchronously.  Primes the audio driver via the already-open
    sidetone OutputStream before handing off to sd.play(), eliminating the
    device-open latency that clipped the first element of every sequence.
    """
    try:
        # 1. Write a tiny silent chunk through the persistent stream so the
        #    driver is warm before sd.play() touches it.
        if _sidetone._stream is not None:
            try:
                warmup = np.zeros(int(SAMPLE_RATE * 0.06), dtype=np.float32)
                _sidetone._stream.write(warmup)
            except Exception:
                pass

        # 2. Play the real audio.
        sd.play(audio, SAMPLE_RATE)
        sd.wait()
    except Exception:
        pass
