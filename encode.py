import subprocess
import os
from pathlib import Path


def convert_to_hls(video_id: str, input_path: str, output_dir: str):
    # Alap mappa létrehozása (pl. hls_output/movie_1)
    base_dir = os.path.join(output_dir, video_id)
    Path(base_dir).mkdir(parents=True, exist_ok=True)

    # A felbontások listája (Név, Szélesség, Magasság, Bitráta)
    renditions = [
        {"name": "360p", "width": 640, "height": 360, "bitrate": "800k"},
        {"name": "480p", "width": 842, "height": 480, "bitrate": "1400k"},
        {"name": "720p", "width": 1280, "height": 720, "bitrate": "2800k"}
    ]

    master_playlist_content = "#EXTM3U\n#EXT-X-VERSION:3\n"

    for r in renditions:
        print(f"--- Feldolgozás: {r['name']} ---")

        # Minden minőségnek külön almappa kell (pl. hls_output/movie_1/720p)
        rendition_dir = os.path.join(base_dir, r['name'])
        Path(rendition_dir).mkdir(parents=True, exist_ok=True)

        output_playlist = os.path.join(rendition_dir, "playlist.m3u8")

        # FFmpeg parancs: Átméretezés (scale) és bitráta beállítás
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-vf", f"scale=w={r['width']}:h={r['height']}:force_original_aspect_ratio=decrease",
            "-c:a", "aac", "-ar", "48000", "-b:a", "128k",  # Hang beállítások
            "-c:v", "h264",  # Videó kodek
            "-profile:v", "main", "-crf", "20",  # Minőség finomhangolás
            "-sc_threshold", "0",  # Fontos HLS-hez
            "-g", "48", "-keyint_min", "48",  # Keyframek beállítása
            "-hls_time", "4",  # 4 másodperces szeletek
            "-hls_playlist_type", "vod",
            "-b:v", r['bitrate'],
            "-maxrate", r['bitrate'],
            "-bufsize", r['bitrate'],  # Buffer méret
            "-hls_segment_filename", f"{rendition_dir}/segment_%03d.ts",
            output_playlist
        ]

        try:
            # Futtatjuk az FFmpeget (ez eltarthat egy ideig!)
            subprocess.run(cmd, check=True)

            # Hozzáadjuk ezt a verziót a Master Playlist szövegéhez
            master_playlist_content += (
                f"#EXT-X-STREAM-INF:BANDWIDTH={int(r['bitrate'].replace('k', '')) * 1000},"
                f"RESOLUTION={r['width']}x{r['height']}\n"
                f"{r['name']}/playlist.m3u8\n"
            )

        except subprocess.CalledProcessError as e:
            print(f"Hiba a {r['name']} generálásakor: {e}")
            return

    # Végül kiírjuk a master.m3u8 fájlt
    master_path = os.path.join(base_dir, "master.m3u8")
    with open(master_path, "w") as f:
        f.write(master_playlist_content)

    print(f"KÉSZ! Master playlist létrehozva: {master_path}")


if __name__ == "__main__":
    # Töröld ki a régi hls_output tartalmát futtatás előtt, hogy tiszta lappal indulj!
    convert_to_hls(
        video_id="movie_1",
        input_path="videos/sample.mp4",
        output_dir="hls_output"
    )