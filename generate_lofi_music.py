import wave
import struct
import numpy as np

def generate_lofi_track(filename="lofi_music.wav", duration_sec=30.0, sample_rate=44100):
    bpm = 82
    beat_dur = 60.0 / bpm
    bar_dur = beat_dur * 4
    total_samples = int(duration_sec * sample_rate)
    
    t = np.linspace(0, duration_sec, total_samples, endpoint=False)
    audio = np.zeros(total_samples, dtype=np.float32)
    
    # 1. Vinyl Crackle / Ambient Texture
    crackle = (np.random.randn(total_samples) * 0.008)
    # Filter crackle to make it warm
    b_lp = np.exp(-2 * np.pi * 3000 / sample_rate)
    crackle_filtered = np.zeros_like(crackle)
    val = 0.0
    for i in range(total_samples):
        val = val * b_lp + crackle[i] * (1 - b_lp)
        crackle_filtered[i] = val
    audio += crackle_filtered * 0.5
    
    # 2. Chord progression frequencies (Cmaj7 -> Am7 -> Dm7 -> G7)
    chords = [
        [261.63, 329.63, 392.00, 493.88], # Cmaj7
        [220.00, 261.63, 329.63, 392.00], # Am7
        [293.66, 349.23, 440.00, 523.25], # Dm7
        [196.00, 246.94, 293.66, 349.23]  # G7
    ]
    
    bass_notes = [130.81, 110.00, 146.83, 98.00] # Roots: C3, A2, D3, G2
    
    # Render Chords & Bass
    num_bars = int(np.ceil(duration_sec / bar_dur))
    for b in range(num_bars):
        bar_start = b * bar_dur
        chord = chords[b % len(chords)]
        bass_freq = bass_notes[b % len(chords)]
        
        # Chord synth (Rhodes style tone: sine + soft 2nd harmonic + lowpass)
        for chord_i, freq in enumerate(chord):
            # Arpeggiated strum effect (stagger chord notes slightly)
            note_start = bar_start + (chord_i * 0.04)
            start_idx = int(note_start * sample_rate)
            end_idx = int(min((bar_start + bar_dur) * sample_rate, total_samples))
            if start_idx < total_samples:
                note_dur = (end_idx - start_idx) / sample_rate
                note_t = np.linspace(0, note_dur, end_idx - start_idx, endpoint=False)
                
                # ADSR Envelope
                env = np.ones_like(note_t)
                attack = int(0.05 * sample_rate)
                decay = int(note_dur * sample_rate)
                if len(env) > attack:
                    env[:attack] = np.linspace(0, 1, attack)
                    env[attack:] = np.exp(-2.5 * (note_t[attack:]))
                
                # Soft rhodes tone
                tone = 0.6 * np.sin(2 * np.pi * freq * note_t) + \
                       0.25 * np.sin(2 * np.pi * freq * 2 * note_t) + \
                       0.15 * np.sin(2 * np.pi * freq * 3 * note_t)
                
                audio[start_idx:end_idx] += tone * env * 0.12

        # Sub-bass
        bass_start_idx = int(bar_start * sample_rate)
        bass_end_idx = int(min((bar_start + bar_dur * 0.95) * sample_rate, total_samples))
        if bass_start_idx < total_samples:
            b_dur = (bass_end_idx - bass_start_idx) / sample_rate
            b_t = np.linspace(0, b_dur, bass_end_idx - bass_start_idx, endpoint=False)
            b_env = np.exp(-1.5 * b_t)
            bass_tone = np.sin(2 * np.pi * bass_freq * b_t)
            audio[bass_start_idx:bass_end_idx] += bass_tone * b_env * 0.22

    # 3. Lo-Fi Drums (Kick on 1 & 3, Snare on 2 & 4, Hi-hats on 8ths)
    total_beats = int(duration_sec / beat_dur)
    for beat in range(total_beats):
        beat_time = beat * beat_dur
        beat_in_bar = beat % 4
        
        # Kick (beats 0 and 2.5)
        kick_times = [beat_time]
        if beat_in_bar == 2:
            kick_times.append(beat_time + (beat_dur * 0.5))
            
        for kt in kick_times:
            k_start = int(kt * sample_rate)
            k_len = int(0.18 * sample_rate)
            k_end = min(k_start + k_len, total_samples)
            if k_start < total_samples:
                kt_arr = np.linspace(0, (k_end - k_start)/sample_rate, k_end - k_start, endpoint=False)
                # Frequency glide 130 -> 45 Hz
                freq_glide = 45 + 85 * np.exp(-30 * kt_arr)
                kick_env = np.exp(-12 * kt_arr)
                kick_wave = np.sin(2 * np.pi * np.cumsum(freq_glide) / sample_rate) * kick_env
                audio[k_start:k_end] += kick_wave * 0.35

        # Snare (beats 1 and 3)
        if beat_in_bar in [1, 3]:
            s_start = int(beat_time * sample_rate)
            s_len = int(0.15 * sample_rate)
            s_end = min(s_start + s_len, total_samples)
            if s_start < total_samples:
                st_arr = np.linspace(0, (s_end - s_start)/sample_rate, s_end - s_start, endpoint=False)
                snare_env = np.exp(-20 * st_arr)
                snare_noise = np.random.randn(len(st_arr)) * snare_env * 0.25
                snare_pop = np.sin(2 * np.pi * 180 * st_arr) * np.exp(-40 * st_arr) * 0.2
                audio[s_start:s_end] += (snare_noise + snare_pop) * 0.6

        # Hi-Hats (eighth notes)
        for hat_i in [0, 0.5]:
            ht_time = beat_time + (hat_i * beat_dur)
            h_start = int(ht_time * sample_rate)
            h_len = int(0.04 * sample_rate)
            h_end = min(h_start + h_len, total_samples)
            if h_start < total_samples:
                ht_arr = np.linspace(0, (h_end - h_start)/sample_rate, h_end - h_start, endpoint=False)
                hat_env = np.exp(-60 * ht_arr)
                hat_noise = np.random.randn(len(ht_arr)) * hat_env
                vol = 0.08 if hat_i == 0 else 0.05
                audio[h_start:h_end] += hat_noise * vol

    # Normalize audio cleanly
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = (audio / max_val) * 0.85

    # Write WAV file
    audio_int16 = (audio * 32767).astype(np.int16)
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())
        
    print(f"Generated upbeat lo-fi track: {filename} ({duration_sec}s)")

if __name__ == "__main__":
    generate_lofi_track()
